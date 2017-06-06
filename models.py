import datetime
import os
import uuid
from collections import OrderedDict
from decimal import Decimal, ROUND_HALF_UP

import markdown
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q

from v3 import constants, services, managers
from v3.services import now
from v3.services import validate_account_agreement_status
from web.collection_utils import collapse_list
from web.markdown_template import MarkdownTemplate
from web.views.validators import less_than_twelve_validator


class SandboxConfig(managers.Model):
    on = models.BooleanField(default=False)
    email_override = models.EmailField()
    date_override = models.DateField(null=True)

    def save(self, *args, **kwargs):
        existing = SandboxConfig.objects.first()
        if existing is not None and existing.pk is not self.pk:
            existing.on = self.on
            existing.email_override = self.email_override
            existing.date_override = self.date_override
            existing.save()
            return existing
        else:
            return super().save(*args, **kwargs)


class Alias(managers.Model):
    name = models.CharField(max_length=100, verbose_name="Alias")
    customer = models.ForeignKey('Customer', related_name="aliases")

    def __str__(self):
        return u'%s' % self.name

    @property
    def identifier(self):
        return self.__str__()


class Counter(managers.Model):
    class Meta:
        abstract = True

    def __str__(self):
        return u'%s' % self.pk


class InvoiceCounter(Counter):
    pass


class QuoteCounter(Counter):
    pass


class Discount(managers.Model):
    """
    Describes a discount rate in percent, often referred to as discount policy.

    These discounts can be created in the configuration menu, and assigned to
    customers.  The sole purpose of this is to provide the default discount
    rate, when adding products to a draft.
    """
    disabled = models.BooleanField(default=False)
    name = models.CharField(max_length=32)
    rate = models.FloatField(verbose_name='Rate (%)', default=0.0)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return u'%s, %s' % (self.name, self.rate) + '%'


class DiscountProxy(managers.FlattenedProxyModel):
    original = models.ForeignKey('Discount')

    disabled = models.BooleanField(default=False)
    name = models.CharField(max_length=32)
    rate = models.FloatField(verbose_name='Rate (%)', default=0.0)
    description = models.TextField(null=True, blank=True)


class CreditPeriod(managers.Model):
    """
    Describes the different payment terms that we offer, e.g. NET 30
    """

    class Meta:
        ordering = ('name',)

    name = models.CharField(max_length=32)
    days = models.IntegerField()

    def __str__(self):
        return u'%s' % self.name


class CreditPeriodProxy(managers.FlattenedProxyModel):
    original = models.ForeignKey('CreditPeriod')

    name = models.CharField(max_length=32)
    days = models.IntegerField()

    def __str__(self):
        return u'%s' % self.name


class Currency(managers.Model):
    """
    Currencies supported by the system, eg. USD, EUR, etc.
    """
    class Meta:
        ordering = ('code',)

    disabled = models.BooleanField(default=False)
    code = models.CharField(max_length=3, primary_key=True)

    objects = managers.DefaultSelectOrPrefetchManager.from_queryset(
        managers.CurrencyQuerySet
    )()

    def __str__(self):
        return u'%s' % self.code


class AddressLabel(managers.Model):
    """
    Stores a label for an address. Labels add some meaning to an address, e.g.
    Main-address, Lawyer address, Sales division, etc.
    """
    address_name = models.CharField(max_length=32)

    class Meta:
        ordering = ['address_name']

    def __str__(self):
        return u'%s' % self.address_name


def full_address_string(a):
    """
    {{ address.postal|linebreaksbr }}<br />
    {{ address.zip }} {{ address.city }}<br />
    {% if address.state %}
        {{ address.state }}<br />
    {% endif %}
    {{ address.get_country_display }}
    :return:
    """
    return "{postal}\n{zip}{city}\n{state}{country}".format(
        postal=a.postal,
        zip=a.zip + ', ' if a.zip else '',
        city=a.city,
        state=a.state + '\n' if a.state else '',
        country=a.get_country_display()
    )


class Address(managers.Model):
    """
    An address with postal, zip, country, etc.
    """
    label = models.ForeignKey('AddressLabel')
    postal = models.TextField()
    zip = models.CharField(max_length=32, blank=True)
    city = models.CharField(max_length=32)
    country = models.CharField(max_length=2, choices=constants.COUNTRIES)
    state = models.CharField(
        max_length=60, null=True, blank=True,
        verbose_name="State/Province"
    )
    custombillto = models.CharField(
        max_length=128,
        verbose_name="Customer name override",
        blank=True
    )
    customer = models.ForeignKey('Customer', related_name='addresses')
    disabled = models.BooleanField(default=False)

    objects = managers.DefaultSelectOrPrefetchManager.from_queryset(
        managers.AddressQuerySet
    )(
        select_related=('label',),
    )

    def __str__(self):
        if len(self.postal) > 50:
            return u'%s, %s..' % (self.label.__str__(), self.postal[:50])
        return u'%s, %s' % (self.label.__str__(), self.postal)

    def full(self):
        return full_address_string(self)

    def save(self, *args, **kwargs):
        # Cleans up the postal field, removing unwanted white-space
        self.postal = os.linesep.join(
            [s for s in self.postal.splitlines() if s.strip()]
        ).strip()
        super().save(*args, **kwargs)

    def get_update_url(self):
        return reverse('address_update', args=[self.customer.pk, self.pk])

    def get_disable_url(self):
        return reverse('address_disable', args=[self.customer.pk, self.pk])


class AddressProxy(managers.FlattenedProxyModel):
    original = models.ForeignKey('Address')

    label = models.CharField(max_length=120)
    postal = models.TextField()
    zip = models.CharField(max_length=32, blank=True)
    city = models.CharField(max_length=32)
    country = models.CharField(max_length=2, choices=constants.COUNTRIES)
    state = models.CharField(max_length=60, null=True, blank=True)
    custombillto = models.CharField(
        max_length=128, verbose_name="Customer name override", blank=True
    )
    customer = models.CharField(max_length=120)
    disabled = models.BooleanField(default=False)

    exclude_fields = [
        'label', 'customer'
    ]

    def refresh_fields(self):
        self.label = self.original.label.address_name
        self.customer = self.original.customer.name
        super().refresh_fields()

    def full(self):
        return full_address_string(self)


class CountryProvincePair(managers.Model):
    country = models.CharField(max_length=2, choices=constants.COUNTRIES)
    province = models.CharField(max_length=60)

    class Meta:
        ordering = ('province',)

    def __str__(self):
        return "%s, %s" % (self.province, self.country)

    def get_disable_url(self):
        return reverse('country_province_pair_delete', args=[self.pk])


def get_random_filename(instance, f_name):
    name, extension = os.path.splitext(f_name)
    # We give an arbitrary name to the file
    f_name = str(uuid.uuid4())
    # We save the name + ext it had in the database
    instance.original_name = "%s%s" % (name, extension)
    # Giving it a nice and organized path
    path = "uploads/files/attachments/misc/{0}{1}"

    if instance.file.customer:
        path = "uploads/files/attachments/{0}/{1}{2}"
        return path.format(instance.file.customer.id, f_name, extension)

    return path.format(f_name, extension)


class File(managers.Model):
    """
    A collection of documents, think: File cabinet
    """
    class Meta:
        ordering = ('-created_at',)

    disabled = models.BooleanField(default=False)
    label = models.CharField(max_length=128)
    keywords = models.ManyToManyField(
        'Keyword', blank=True, related_name='file_set', verbose_name='Keywords'
    )
    customer = models.ForeignKey(
        'Customer', null=True, blank=True, related_name='files'
    )
    user = models.ForeignKey(User, blank=True, null=True, related_name='files')

    objects = managers.DefaultSelectOrPrefetchManager.from_queryset(
        managers.FileQuerySet
    )(
        select_related=('customer',),
        prefetch_related=('keywords',)
    )

    def __str__(self):
        return '{}, {}'.format(self.identifier, self.label)

    @property
    def identifier(self):
        return 'FIL-{}'.format(self.pk)

    @property
    def status(self):
        return 'Disabled' if self.disabled else 'Enabled'

    def get_absolute_url(self):
        if self.customer:
            return reverse('file_detail', args=[self.customer.pk, self.pk])
        else:
            return reverse('global_file_detail', args=[self.pk])

    def get_disable_url(self):
        if self.customer:
            return reverse('file_delete', args=[self.customer.pk, self.pk])
        else:
            return reverse('global_file_delete', args=[self.pk])


class Attachment(managers.Model):
    """
    The actual file inside the File object (file cabinet)
    """
    # 1) The physical file itself which is stored under an arbitrary name
    data = models.FileField(verbose_name='File path', upload_to=get_random_filename)
    # 2) The original file name
    original_name = models.CharField(max_length=200, blank=True, null=True, verbose_name='File name')
    # NOTE: It is important to have the file name AFTER the file, otherwise the upload_to does not work. Go figure.

    file = models.ForeignKey(File, null=True, related_name='attachments')
    disabled = models.BooleanField(default=False)
    user = models.ForeignKey(User, null=True, blank=True, related_name='attachments')

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        result = u'%s'
        return result % self.original_name if self.original_name else result % os.path.basename(self.data.name)

    @property
    def identifier(self):
        return "ATC-%s" % self.id

    def file_extension(self):
        name, extension = os.path.splitext(self.data.name)
        return str(extension).upper()

    def get_absolute_url(self):
        return reverse('file_detail', args=[self.file.customer.pk, self.file.pk])


class CustomerReputation(managers.Model):
    """
    Many to many relation table between Customer and Reputation.
    This overrides django's m2m table, adding the possibility to have one or more fields in the relation
    """
    customer = models.ForeignKey('Customer')
    reputation = models.ForeignKey('Reputation', related_name="customer_reputation")
    assignment_reason = models.CharField(max_length=200,
                                         blank=True,
                                         null=True,
                                         help_text="The reason why this customer has been assigned with this tag.")

    objects = managers.DefaultSelectOrPrefetchManager.from_queryset(
        managers.KeywordQuerySet
    )()

    def get_reason(self):
        return self.assignment_reason

    def get_html_id(self):
        """
        THis method provides a work around to the HTML we have in the customer details page. Through this method we can
        Set the HTML object ID similar to he TAG generated for each reputation tag
        :return:
        """
        return "tg-rep-" + self.reputation.tag_name.lower().replace(" ", "-")


class Reputation(managers.Model):
    """
    Stores reputation tags for models
    """

    CRITICAL_LEVEL = 'CW'
    WARNING_LEVEL = 'MW'
    NORMAL_LEVEL = 'SW'

    WARNING_CHOICES = (
        (CRITICAL_LEVEL, 'Critical Warning'),
        (WARNING_LEVEL, 'Medium Warning'),
        (NORMAL_LEVEL, 'Simple Warning'),
    )

    tag_name = models.CharField(max_length=120)
    description = models.CharField(max_length=120, blank=True, null=True)
    warning_level = models.CharField(choices=WARNING_CHOICES, max_length=2)
    disabled = models.BooleanField(default=False)

    objects = managers.DefaultSelectOrPrefetchManager.from_queryset(
        managers.KeywordQuerySet
    )()

    class Meta:
        ordering = ('tag_name',)

    def __str__(self):
        return u'%s' % self.tag_name


class Keyword(managers.Model):
    """
    Keywords are tags that can be applied to a lot of objects within the app.
    This makes objects easier to search for and filter.
    """
    word = models.CharField(max_length=120)
    disabled = models.BooleanField(default=False)

    objects = managers.DefaultSelectOrPrefetchManager.from_queryset(
        managers.KeywordQuerySet
    )()

    class Meta:
        ordering = ('word',)

    def __str__(self):
        return u'%s' % self.word


class Customer(managers.Model):
    """
    A Customer represents a real customer with addresses, contact, invoices and
    agreements.  All business data in the application is linked to a customer
    directly or indirectly
    """
    name = models.CharField(max_length=120, unique=True, db_index=True, verbose_name='Name')
    description = models.TextField(blank=True)
    vat_number = models.CharField(
        max_length=32, blank=True, verbose_name='VAT number',
        help_text='European VAT numbers are formatted as "DK123456".'
    )
    currency = models.ForeignKey('Currency', related_name='customers')
    payment_account = models.ForeignKey(
        'PaymentAccount', related_name='customers'
    )
    main_address = models.ForeignKey(
        'Address', related_name='main_address_customer', null=True
    )
    billing_address = models.ForeignKey('Address', related_name='billing_address_customer', null=True)
    shipping_address = models.ForeignKey('Address', related_name='shipping_address_customer', null=True)
    discount_policy = models.ForeignKey('Discount', null=True, blank=True)
    credit_period = models.ForeignKey('CreditPeriod')
    shipping_info = models.TextField(blank=True)
    invoice_info = models.TextField(blank=True)
    keywords = models.ManyToManyField('Keyword', blank=True, related_name='customers')
    end_customers = models.ManyToManyField('Customer', related_name='resellers')
    reputation = models.ManyToManyField('Reputation', blank=True, through='CustomerReputation', related_name='reputation')

    objects = managers.DefaultSelectOrPrefetchManager.from_queryset(managers.CustomerQuerySet)(
        prefetch_related=('end_customers',)
    )

    def __str__(self):
        return '{} {}'.format(self.identifier, self.name)

    @property
    def identifier(self):
        return u'CUS-{}'.format(self.pk)

    def is_european(self):
        return services.customer_is_european(self)

    def get_absolute_url(self):
        return reverse('customer_detail', args=[self.pk])

    def get_match_url(self):
        return reverse('customer_payments_match', args=[self.pk])

    def api_actions(self):
        actions = {}
        remove_end_customers = {}
        for end_customer in self.end_customers.all():
            remove_end_customers[str(end_customer.pk)] = {
                'remove': reverse('customer_remove_end_customer', args=[self.pk, end_customer.pk])
            }

        actions['end_customers'] = remove_end_customers
        return actions

    def get_warning_level(self):
        if not self.reputation.all().count():
            return None

        reputation = self.reputation.order_by('warning_level').first()

        if reputation.warning_level == Reputation.CRITICAL_LEVEL:
            return "danger"
        if reputation.warning_level == Reputation.WARNING_LEVEL:
            return "warning"
        if reputation.warning_level == Reputation.NORMAL_LEVEL:
            return "info"


class CustomerProxy(managers.FlattenedProxyModel):
    original = models.ForeignKey('Customer', related_name='proxies')
    name = models.CharField(max_length=120)
    customer_number = models.IntegerField()
    description = models.TextField(blank=True)
    vat_number = models.CharField(max_length=32, blank=True, verbose_name='Vat number')
    currency_code = models.CharField(max_length=3)
    main_address = models.OneToOneField('AddressProxy', related_name='proxy_main_address_customer', null=True)
    billing_address = models.OneToOneField('AddressProxy', related_name=''
                                                                        ''
                                                                        'proxy_billing_address_customer', null=True)
    shipping_address = models.OneToOneField('AddressProxy', related_name='proxy_shipping_address_customer', null=True)
    discount_policy = models.OneToOneField('DiscountProxy', null=True, blank=True)
    credit_period = models.OneToOneField('CreditPeriodProxy')
    shipping_info = models.TextField(blank=True)
    invoice_info = models.TextField(blank=True)

    exclude_fields = [
        'customer_number',
        'currency_code'
    ]

    def __str__(self):
        return '{} {}'.format(self.identifier, self.name)

    @property
    def identifier(self):
        return u'CUS-{}'.format(self.customer_number)

    def refresh_fields(self):
        self.customer_number = self.original.pk
        self.currency_code = self.original.currency.code
        if self.discount_policy is None and self.original.discount_policy is not None:
            self.discount_policy = services.create_flattened_proxy_model(DiscountProxy, self.original.discount_policy)
        if self.main_address is None and self.original.main_address is not None:
            self.main_address = services.create_flattened_proxy_model(AddressProxy, self.original.main_address)
        if self.billing_address is None and self.original.billing_address is not None:
            self.billing_address = services.create_flattened_proxy_model(AddressProxy, self.original.billing_address)
        if self.shipping_address is None and self.original.shipping_address is not None:
            self.shipping_address = services.create_flattened_proxy_model(AddressProxy, self.original.shipping_address)
        super().refresh_fields()


class Contact(managers.Model):
    """
    While the Customer class refers to a company or institution, a contact
    refers to a certain person within such institution
    """
    class Meta:
        ordering = ('first_name', 'last_name')

    customer = models.ForeignKey('Customer', related_name="contacts")
    first_name = models.CharField(max_length=120)
    middle_name = models.CharField(max_length=120, null=True, blank=True)
    last_name = models.CharField(max_length=120)
    email = models.EmailField(max_length=120, blank=True)
    phone = models.CharField(max_length=32, blank=True)
    mobile = models.CharField(max_length=32, blank=True)
    fax = models.CharField(max_length=32, blank=True)
    disabled = models.BooleanField(default=False)

    objects = managers.DefaultSelectOrPrefetchManager.from_queryset(managers.ContactQuerySet)(
        select_related=('customer',)
    )

    @property
    def fullname(self):
        res = self.first_name
        if self.middle_name:
            res += " " + self.middle_name
        res += " " + self.last_name
        return res

    @property
    def identifier(self):
        return "CON-{}".format(self.pk)

    def __str__(self):
        res = self.fullname
        if self.email:
            res += ", " + self.email
        return res

    def get_absolute_url(self):
        return reverse('contact_detail', args=[self.customer.pk, self.pk])

    def get_update_url(self):
        return reverse('contact_update', args=[self.customer.pk, self.pk])

    def get_disable_url(self):
        return reverse('contact_disable', args=[self.customer.pk, self.pk])

    def status(self):
        return 'Active' if not self.disabled else 'Disabled'


class ContactProxy(managers.FlattenedProxyModel):
    original = models.ForeignKey('Contact')

    customer = models.CharField(max_length=120)
    first_name = models.CharField(max_length=120)
    middle_name = models.CharField(max_length=120, null=True, blank=True)
    last_name = models.CharField(max_length=120)
    email = models.EmailField(max_length=120, blank=True)
    phone = models.CharField(max_length=32, blank=True)
    mobile = models.CharField(max_length=32, blank=True)
    fax = models.CharField(max_length=32, blank=True)
    disabled = models.BooleanField(default=False)

    exclude_fields = [
        'customer'
    ]

    @property
    def fullname(self):
        res = self.first_name
        if self.middle_name:
            res += " " + self.middle_name
        res += " " + self.last_name
        return res

    def refresh_fields(self):
        self.customer = self.original.customer.name
        super().refresh_fields()

    @property
    def identifier(self):
        return 'CIP-{}'.format(self.pk)

    def __str__(self):
        return '{} {} {}'.format(self.identifier, self.first_name, self.last_name)


class Account(managers.Model):
    """
    Accounts are an abstraction of license owners. All licenses are bound to exactly one account.
    An account is managed by an arbitrary number of contacts, one of which are designated the
    main contact. Contacts are bound to customers.
    """
    STATUS_ACTIVE = 'Active'
    STATUS_DISABLED = 'Disabled'

    disabled = models.BooleanField(default=False)

    label = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    main_contact = models.ForeignKey(Contact, related_name="main_contact_accounts")
    contacts = models.ManyToManyField(Contact, related_name="secondary_contact_accounts",
                                      verbose_name="Secondary contacts", blank=True)
    customer = models.ForeignKey('Customer', null=True, related_name='accounts')
    agreement = models.ForeignKey('Agreement', related_name='accounts')
    discount_policy = models.ForeignKey('Discount', null=True, blank=True)

    keywords = models.ManyToManyField('Keyword', blank=True, related_name='accounts')
    last_summary_date = models.DateTimeField(null=True, default=None)

    objects = managers.DefaultSelectOrPrefetchManager.from_queryset(managers.AccountQuerySet)(
        select_related=('customer', 'main_contact', 'main_contact__customer', 'agreement')
    )

    @property
    def status(self):
        return self.STATUS_DISABLED if self.disabled else self.STATUS_ACTIVE

    def get_absolute_url(self):
        return reverse('account_detail', args=[self.customer.pk, self.pk])

    def get_main_contact_information(self):
        return '' if not self.main_contact else self.main_contact

    @property
    def get_active_licenses_count(self):
        return self.items.active_with_invoice().distinct().count()

    @property
    def identifier(self):
        return "ACT-{}".format(self.pk)

    def __str__(self):
        return "{}, {}, {}".format(self.identifier, self.label, self.main_contact)

    @property
    def simple_label(self):
        return "{}, {}".format(self.identifier, self.label)


class Option(managers.Model):
    """
    Option stores special options such as default template or default maintenance end date.
    It is a simple key value store (strings).
    """
    key = models.CharField(max_length=32, primary_key=True)
    value = models.TextField()

    objects = managers.DefaultSelectOrPrefetchManager.from_queryset(managers.OptionQuerySet)()

    def __str__(self):
        return u'%s' % self.key


class Vat(managers.Model):
    """
    Describes a VAT model, which can be used by items/invoices.
    """
    class Meta:
        ordering = ('name',)

    creator = models.ForeignKey(User, blank=True, null=True, related_name="vat_created", default=None)
    updater = models.ForeignKey(User, blank=True, null=True, related_name="vat_updated", default=None)

    name = models.CharField(max_length=32, unique=True)
    rate = models.FloatField(verbose_name='Rate (%)', default=0.0)
    message = models.TextField()
    disabled = models.BooleanField(default=False)

    objects = managers.DefaultSelectOrPrefetchManager.from_queryset(managers.VatQuerySet)()

    def __str__(self):
        return u'%s %s' % (self.name, self.rate)


class PaymentAccount(managers.Model):
    """
    Simply a label to manage payments from different sources, that is, a
    Customer pays to our Danske Bank account and another pays in cash.
    Then we manage the in-system payment_accounts to match the actual payments.
    """
    name = models.CharField(max_length=120)
    currency = models.ForeignKey('Currency', default=1)
    description = models.TextField()
    payment_info = models.TextField(default="")
    disabled = models.BooleanField(default=False)

    objects = managers.DefaultSelectOrPrefetchManager.from_queryset(managers.PaymentAccountQuerySet)()

    @property
    def payment_info_rendered(self):
        return markdown.markdown(self.payment_info, extensions=['markdown.extensions.extra'])

    @property
    def identifier(self):
        return 'PAC-{}'.format(self.pk)

    def __str__(self):
        return '{} {} ({})'.format(self.identifier, self.name, self.currency)


class PaymentAccountProxy(managers.FlattenedProxyModel):
    original = models.ForeignKey('PaymentAccount')
    name = models.CharField(max_length=120)
    currency = models.CharField(max_length=3)
    description = models.TextField()
    payment_info = models.TextField(default="")

    exclude_fields = [
        'currency'
    ]

    def refresh_fields(self):
        self.currency = self.original.currency.code
        super().refresh_fields()

    @property
    def payment_info_rendered(self):
        return markdown.markdown(self.payment_info, extensions=['markdown.extensions.extra'])

    @property
    def identifier(self):
        return 'PAC-{}'.format(self.pk)

    def __str__(self):
        return '{} {}'.format(self.identifier, self.name)


class Allocation(managers.Model):
    """
    Allocation of payments to invoices as a many-to-many relationship.
    """
    class Meta:
        ordering = ('-pk',)

    invoice = models.ForeignKey('Invoice', related_name='allocations')
    payment = models.ForeignKey('Payment', related_name='allocations')
    date = models.DateField(null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reverse = models.OneToOneField('Allocation', blank=True, null=True, related_name='reversed_allocation')
    user = models.ForeignKey(User, null=True, blank=True)

    objects = managers.DefaultSelectOrPrefetchManager.from_queryset(managers.AllocationQuerySet)()

    def __str__(self):
        return u'ALC-%s' % self.pk

    @property
    def identifier(self):
        return 'ALC-{}'.format(self.pk)

    def get_reverse_url(self):
        return reverse('customer_allocation_reverse', args=[self.payment.customer.pk, self.pk])

    def get_absolute_url(self):
        return self.payment.customer.get_absolute_url() + '#payments'

    def save(self, *args, **kwargs):
        _now = now()
        if not self.date:
            self.date = _now
        super().save(*args, **kwargs)

    @property
    def is_reverse(self):
        return self.reversed_allocation is not None

    @property
    def is_reversed(self):
        return self.reverse is not None


class Payment(managers.Model):
    """
    An entry of currency into, or out of, the system. Two numbers are given.
    'amount' is the amount we use in the system, while 'received' is the actual
    number on our account. Sometimes we want 1000,- but get 997,- because of
    taxes. In this case, 'amount' is 1000 and 'received' is 997.

    A payment can optionally link to a file belonging to the customer.
    """

    class Meta:
        ordering = ('-pk',)

    date = models.DateField()
    payment_account = models.ForeignKey('PaymentAccount')
    customer = models.ForeignKey('Customer', related_name='payments')
    currency = models.ForeignKey('Currency')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Full amount')  # The amount used internally
    received = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Net amount')  # The amount actually received
    reverse = models.OneToOneField('Payment', blank=True, null=True, related_name='reversed_payment')

    # Stored fields
    allocated = models.DecimalField(max_digits=10, decimal_places=2, default=0.)
    residual = models.DecimalField(max_digits=10, decimal_places=2, default=0.)

    objects = managers.DefaultSelectOrPrefetchManager.from_queryset(managers.PaymentQuerySet)(
        select_related=('customer', 'currency',),
        prefetch_related=('allocations', 'allocations__invoice',)
    )

    def __str__(self):
        return u'PAY-%s' % self.pk

    @property
    def identifier(self):
        return 'PAY-{}'.format(self.pk)

    def entry_date(self):
        return self.created_at.date()

    def refresh_values(self):
        self.allocated = self._allocated()
        self.residual = self._residual()

    def get_verbose_type(self):
        return "Payment"

    def _residual(self):
        return self.amount - self.allocated

    def _allocated(self):
        """
        The allocated sum is defined as the sum of all allocations minus the amount of
        the reverse or reversed_payment if this one.
        """
        allocation_sum = self.allocations.aggregate(models.Sum('amount'))['amount__sum'] or 0
        rev_amount = 0
        if self.reverse:
            rev_amount = self.reverse.amount
        try:
            rev_amount = self.reversed_payment.amount
        except ObjectDoesNotExist:
            pass
        return Decimal(allocation_sum - rev_amount)

    def get_reverse_url(self):
        return reverse('customer_payments_reverse', args=[self.customer.pk, self.pk])

    @property
    def is_reverse(self):
        return self.reversed_payment is not None

    @property
    def is_reversed(self):
        return self.reverse is not None

    def get_absolute_url(self):
        return reverse('payment_detail', args=[self.id])

    @property
    def get_date(self):
        # Sets date the earliest possible so Accounts Payment Summary will always sort Payments before Invoices
        return datetime.datetime(self.date.year, self.date.month, self.date.day, 23, 59, 59)

    @property
    def get_total(self):
        return self.amount


class Product(managers.Model):
    """
    Describes a product. A product is the template from which an Item is made.
    Items are what is actually sold, which is why Product does not have a
    license name
    """
    ordering = models.IntegerField(default=0)

    name = models.CharField(max_length=16, verbose_name="Part ID")
    description = models.TextField(verbose_name='Description')
    main_description = models.TextField(verbose_name='Maintenance description', blank=True, null=True)
    backmain_description = models.TextField(verbose_name='Back-maintenance description', blank=True, null=True)
    disabled = models.BooleanField(default=False)

    objects = managers.DefaultSelectOrPrefetchManager.from_queryset(managers.ProductQuerySet)()

    class Meta:
        ordering = ['ordering']

    def __str__(self):
        return u'%s' % self.name

    @property
    def identifier(self):
        return "PRO-%s" % self.id

    def latest_price(self, currency):
        return self.product_prices.filter(currency=currency).last().price


class ProductPrice(managers.Model):
    """
    Describes a price for a product with its currency and value. An item of
    type Product can only be sold in a certain currency if a ProductPrice for that
    Product and Currency exists
    """
    currency = models.ForeignKey(Currency)
    product = models.ForeignKey(Product, related_name="product_prices")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    maintenance_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Annual maintenance fee',
        blank=True,
        null=True
    )
    backmaintenance_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Annual back maintenance fee',
        blank=True,
        null=True
    )

    objects = managers.DefaultSelectOrPrefetchManager.from_queryset(managers.ProductPriceQuerySet)()


class ItemInv(managers.Model):
    """
    Item-Invoice. Relates items to invoices, as an Item can be represented on multiple invoices.

    This objects lets us know where an item has been drafted, quoted, sold, etc. without having
    to change anything on the item itself. This lets us keep the table for the items very clean,
    and makes it so that all rows correspond to one specific item.
    """
    item = models.ForeignKey('Item')
    invoice = models.ForeignKey('Invoice')
    disabled = models.BooleanField(default=False)
    reverse = models.ForeignKey('ItemInv', null=True, blank=True, default=None)

    objects = managers.DefaultSelectOrPrefetchManager.from_queryset(managers.ItemInvQuerySet)()

    class Meta:
        unique_together = (('item', 'invoice'),)

    @property
    def identifier(self):
        return 'ITI-{}'.format(self.pk)

    def __str__(self):
        return '{}'.format(self.identifier)


class Item(managers.Model):

    # License status
    STATUS_DISABLED = "Disabled"
    STATUS_ACTIVE = "Active"

    # Maintenance status
    STATUS_EXPIRING_VERBOSE = "Expires in %s day(s)"
    STATUS_EXPIRING = "Expiring"
    STATUS_EXPIRED = "Expired"
    STATUS_NEXISTENT = "Never Extended"

    # Origin status
    STATUS_ORIGIN_IMPORTED = "Imported"
    STATUS_ORIGIN_INVOICE = "Invoice"

    # Renewable status
    STATUS_RENEWABLE = "Yes"
    STATUS_NRENEWABLE = "No"
    STATUS_RENEWABLE_VERBOSE = "Renewable"
    STATUS_NRENEWABLE_VERBOSE = "Not Renewable"

    """
    Stores sold softwares and its information, such as LICENSES
    """

    serial = models.AutoField(primary_key=True)  # Software license
    product = models.ForeignKey('Product', verbose_name='Product')
    account = models.ForeignKey('Account', verbose_name='Account', related_name='items')
    imported = models.BooleanField(default=False)
    expiry_date = models.DateField(verbose_name='Maintenance expiry')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.FloatField(default=0.0, verbose_name='Discount rate')
    description = models.TextField()
    vat = models.ForeignKey('Vat', null=True)  # Null is for imported licenses
    vat_rate = models.FloatField(default=0.)  # For storing snapshot of Vat rate
    vat_message = models.TextField()
    disabled = models.BooleanField(default=False)  # To activate/deactivate license
    renewable = models.BooleanField(default=False)  # Set to False if customer does not want renewal
    in_summary = models.BooleanField(default=True)  # Set to False if license should not be shown in summary

    # Static data used for license summary on invoices
    static_account_label = models.CharField(max_length=256)
    static_customer_label = models.CharField(max_length=256)
    static_agreement_label = models.CharField(max_length=256)

    # Calculations
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    objects = managers.DefaultSelectOrPrefetchManager.from_queryset(managers.ItemQuerySet)(
        # Had to remove 'vat' from this list, since it was giving issues with ReportCreateForm
        # http://stackoverflow.com/questions/42697045/annotate-causes-programmingerror-must-appear-in-the-group-by-clause-or-be-used
        select_related=(
            'product',
            'account',
            'account__customer',
            'account__agreement',
        )
    )

    class Meta:
        ordering = ['serial']

    def get_absolute_url(self):
        return reverse('license_detail', args=[self.pk])

    def latest_document(self):
        """
        Gets the latest document, which is not an invoice nor a draft
        :return:
        """
        # Gets the latest document this item was seen
        latest_invoice = Invoice.objects.filter(Q(type=Invoice.TYPE_QUOTE),
                                                iteminv__item=self).last()
        # Gets the latest document its maintenance was seen
        latest_maintenance = Maintenance.objects.filter(Q(invoice__type=Invoice.TYPE_QUOTE),
                                                        serial=self
                                                        ).last()

        # Returns the latest if the maintenance has a different invoice from item's
        if latest_maintenance:
            return latest_maintenance.invoice if latest_maintenance.invoice != latest_invoice else None
        return None

    @property
    def flag(self):
        return self.STATUS_RENEWABLE if self.renewable else self.STATUS_NRENEWABLE

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.refresh_static_labels()
        return super(Item, self).save(*args, **kwargs)

    def refresh_static_labels(self):
        self.vat_rate = self.vat.rate if self.vat is not None else self.vat_rate
        self.vat_message = self.vat.message if self.vat is not None else self.vat_message
        self.static_account_label = str(self.account)
        self.static_customer_label = str(self.account.customer)
        self.static_agreement_label = str(self.account.agreement)

    def refresh_values(self):
        # Subtotal
        if self.discount:
            self.subtotal = (
                self.price * Decimal(str((100.0 - self.discount) / 100.0))
            ).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
        else:
            self.subtotal = Decimal(str(self.price))

        # Total
        self.total = (
            self.subtotal * Decimal(
                str(1.0 + (self.vat_rate / 100.0))
            )
        ).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)

    @property
    def invoice(self):
        # Gets the latest invoice this item has been seen
        return Invoice.objects.filter(iteminv__item=self, iteminv__invoice__type=Invoice.TYPE_INVOICE).last()

    @property
    def status(self):
        return self.STATUS_ACTIVE if not self.disabled else self.STATUS_DISABLED

    def get_start_date(self):
        # If it has maintenance
        if self.has_maintenance:
            # If it was imported and does not have extended maintenance on invoices
            if self.imported and not self.maintenances.has_invoice().active().exists():

                # A change in Imports class now allows users to specify a start date.
                import_maintenance_start = self.importItems.all().first().maintenance_start
                if import_maintenance_start:
                    return import_maintenance_start

                # (Before change in Import class)
                creation_date = self.importItems.all().first().created_at.date()
                # Sometimes, items are imported and the date of import is bigger than the expiry date
                # To solve this problem, in case the expiry_date is inferior to the import creation's date
                # we show the expiry date, since the license will be expired anyway
                if self.get_expiry_date() < creation_date:
                    return self.get_expiry_date()
                return creation_date
            # If it is not imported return the expiry date, which is the day after the item was put into the system
            return self.maintenances.active().has_invoice().last().start
        return self.expiry_date

    def get_expiry_date(self):
        return self.expiry_date

    @property
    def has_maintenance(self):
        """
        Checks if item has maintenance. Due to an error in the project design, imported items does not hold maintenance relations
        the first time they are created. Therefore this special case needs to be treated.
        :return:
        """
        if self.imported:
            return True
        return self.maintenances.has_invoice().active().exists()

    @property
    def is_maintenance_expired(self):
        return self.get_expiry_date() < services.now().date()

    def maintenance_status(self, verbose=False):
        # Today
        today = services.now().date()
        # The difference between the maintenance end's date and today's
        date_difference = (self.get_expiry_date() - today).days

        # If the difference between today and the expiry date is < 0, then the maintenance is expired, else is expiring
        if services.get_system_maintenance_expiring_days() > date_difference > 0:
            return self.STATUS_EXPIRING_VERBOSE % date_difference if verbose else self.STATUS_EXPIRING

        # If the maintenance end is bigger than today (At this point, if it's not expiring then it's active)
        if self.get_expiry_date() > today:
            return self.STATUS_ACTIVE

        # If none of the above, then it must be expired
        return self.STATUS_EXPIRED

    @property
    def is_maintenance_expiring(self):
        return self.maintenance_status() == self.STATUS_EXPIRING

    @property
    def maintenance_status_verbose(self):
        return self.maintenance_status(True)

    @property
    def origin(self):
        return self.importItems.first() if self.imported else self.invoice

    def get_origin_url(self):
        if self.origin:
            return self.origin.get_absolute_url()
        return ''

    @property
    def quoted_maintenance(self):
        """
        If item has maintenance on a non-expired quote, return that maintenance object. Otherwise None
        """
        return Maintenance.objects.on_a_non_expired_quote().for_item(self)

    @property
    def identifier(self):
        return u'PSN-' + str(self.serial)

    def __str__(self):
        return self.identifier

    def __int__(self):
        return int(self.serial)

    def matches(self, other):
        """
        takes another Item, and returns True if self can be on the same invoice
        row as other, that is, they are of the same product and so on.
        """
        return (self.product == other.product and
                self.price == other.price and
                self.vat == other.vat and
                self.discount == other.discount)

    def get_renewable_status(self):
        return "Yes" if self.renewable else "No"


class LicenseDisable(managers.Model):
    """
    This object keeps track of disabled licenses. When licenses are disabled
    and object like this is created. The object keeps references to the disabled
    licenses as well as a File in which the reason for disabling the licenses
    can be found.
    """
    customers = models.ManyToManyField('Customer', related_name='deactivations')
    licenses = models.ManyToManyField('Item', blank=True)
    user = models.ForeignKey(User, null=True)

    def __str__(self):
        return 'DAC-{}'.format(self.pk)

    @property
    def identifier(self):
        return self

    def get_absolute_url(self):
        return reverse('deactivation_detail', args=[self.id])


class Maintenance(managers.Model):
    serial = models.ForeignKey('Item', related_name='maintenances')
    back = models.BooleanField(default=False, verbose_name='Back maintenance')
    start = models.DateField(verbose_name='Start date')
    end = models.DateField(verbose_name='End date')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.FloatField(default=0.0)
    vat = models.ForeignKey(Vat)
    invoice = models.ForeignKey('Invoice', related_name='maintenances')
    disabled = models.BooleanField(default=False)
    description = models.TextField(verbose_name='Maintenance description', blank=True, null=True)
    back_description = models.TextField(verbose_name='Back-maintenance description', blank=True, null=True)
    reverse = models.ForeignKey('Maintenance', related_name='rev_set', null=True, default=None)

    # Static labels
    vat_rate = models.FloatField(default=0.)  # For storing snapshot of Vat rate
    vat_message = models.TextField()

    # calculations
    days = models.IntegerField(default=0)
    quantity = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    subtotal_by_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_by_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    objects = managers.DefaultSelectOrPrefetchManager.from_queryset(managers.MaintenanceQuerySet)(
        select_related=(
            'serial', 'vat', 'serial__vat',
            'serial__account', 'serial__product',
            'serial__account__customer',
            'serial__account__agreement',
        )
    )

    def save(self, *args, suppress_labels=False, **kwargs):
        if self.pk is None and not suppress_labels:
            self.refresh_static_labels()
        return super().save(*args, **kwargs)

    def refresh_static_labels(self):
        self.vat_rate = self.vat.rate
        self.vat_message = self.vat.message

    def refresh_values(self):
        self.days = (self.end - self.start).days + 1
        self.quantity = (Decimal(self.days) / Decimal(365)).quantize(Decimal('.0001'), rounding=ROUND_HALF_UP)

        # Subtotal
        if self.discount:
            self.subtotal = (
                self.price * Decimal(
                    str((100.0 - self.discount) / 100.0)
                )
            ).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
        else:
            self.subtotal = Decimal(str(self.price))
        self.subtotal_by_quantity = (self.subtotal * self.quantity).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)

        # Total
        self.total = (
            self.subtotal * Decimal(
                str(1.0 + (self.vat_rate / 100.0))
            )
        ).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
        self.total_by_quantity = (
            self.subtotal_by_quantity * Decimal(
                str(1.0 + (self.vat_rate / 100.0))
            )
        ).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)

    def matches(self, other):
        """
        takes another Maintenance, and returns True if self can be on the same invoice
        row as other, that is, they are of the same product and so on.
        """
        return (self.serial.product == other.serial.product and
                self.price == other.price and
                self.vat == other.vat and
                self.discount == other.discount and
                self.start == other.start and
                self.end == other.end)

    def __str__(self):
        return u'%s' % self.serial.__str__()

    def __int__(self):
        return int(self.serial)


class CustomItemAssociation(managers.Model):
    """
    Custom item association. As custom items need a notion of products.
    Used for internal reporting use only.
    """
    citem = models.ForeignKey('CustomItem', related_name='assocs')
    product = models.ForeignKey(Product)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    count = models.IntegerField()


class CustomItem(managers.Model):
    """
    A Custom item is an item that can be sold, which does not related to the Items,
    which represent product licenses and cannot have maintenance. This could cover
    things like fees, royalties, donations and other things like that.

    Custom items are linked to a product through CustomItemAssociations. This is
    a way for us to know how to include Custom items in reports.
    """
    name = models.CharField(max_length=128, verbose_name='Name')
    invoice = models.ForeignKey('Invoice', related_name='citems')
    account = models.ForeignKey('Account', null=True, blank=True, default=None)
    vat = models.ForeignKey('Vat')
    disabled = models.BooleanField(default=False)

    # static labels
    vat_rate = models.FloatField(default=0.)
    vat_message = models.TextField()
    agreement = models.TextField(default='')

    objects = managers.DefaultSelectOrPrefetchManager.from_queryset(managers.CustomItemQuerySet)()

    def save(self, *args, suppress_labels=False, **kwargs):
        if self.pk is None and not suppress_labels:
            self.refresh_static_labels()
        super().save(*args, **kwargs)

    def refresh_static_labels(self):
        self.vat_rate = self.vat.rate
        self.vat_message = self.vat.message
        self.agreement = str(self.account.agreement) if self.account else ''

    @property
    def price(self):
        assocs = CustomItemAssociation.objects.filter(citem=self)
        return assocs.aggregate(models.Sum('price'))['price__sum']  # Don't use count

    @property
    def total(self):
        return Decimal(float(self.price) * (1.0 + (self.vat_rate / 100.0)))

    def __str__(self):
        return self.name

    @property
    def identifier(self):
        return u'CIT-%s' % self.id


class Invoice(managers.Model):
    """
    An invoice is an object containing any information relating to a sale.
    The invoice is the main asset of the application and has a lot of pointers
    to all other data
    """

    TYPE_DRAFT = "d"
    TYPE_QUOTE = "q"
    TYPE_INVOICE = "i"

    class Meta:
        ordering = ('-invoice_number', '-quote_number', '-pk')

    INVOICE_TYPES = (
        (TYPE_DRAFT, "Draft"),
        (TYPE_QUOTE, "Quote"),
        (TYPE_INVOICE, "Invoice"),
    )

    invoice_number = models.ForeignKey('InvoiceCounter', null=True, blank=True, default=None)
    quote_number = models.ForeignKey('QuoteCounter', null=True, blank=True, default=None)
    template = models.ForeignKey('Template')
    # The customer for this invoice. Assigned through a Proxy, which then connects to a customer
    customer = models.OneToOneField('CustomerProxy', related_name='invoices')
    end_customer = models.OneToOneField(
        'CustomerProxy', related_name='end_customer_invoice',
        null=True, blank=True, verbose_name='End customer'
    )
    contact = models.OneToOneField('ContactProxy', related_name='proxy_contact')
    quote_date = models.DateField(verbose_name='Quote date')
    quote_expiry = models.DateField(verbose_name='Quote expiry date')
    invoice_date = models.DateTimeField(null=True, blank=True)
    type = models.CharField(max_length=1, choices=INVOICE_TYPES, default='d')
    currency = models.ForeignKey('Currency')
    customer_reference = models.ForeignKey('File', null=True, blank=True)
    customer_address = models.OneToOneField('AddressProxy', related_name='inv_cust_address', null=True, blank=True)
    billing_address = models.OneToOneField('AddressProxy', related_name='inv_billing_address', null=True, blank=True)
    shipping_address = models.OneToOneField('AddressProxy', related_name='inv_shipping_address', null=True, blank=True)
    shipping_att = models.OneToOneField(
        'ContactProxy', null=True, blank=True, verbose_name="Ship-to Att.",
        related_name="proxy_shipping_att"
    )
    billing_att = models.OneToOneField(
        'ContactProxy', null=True, blank=True, verbose_name="Bill-to Att.",
        related_name="proxy_billing_att"
    )
    sold_by = models.ForeignKey(User, related_name='sold_by', null=True, blank=True)
    credit_period = models.OneToOneField('CreditPeriodProxy')
    disabled = models.BooleanField(default=False)
    # Reverse invoice - Credited invoice
    creditted_by = models.OneToOneField('Invoice', null=True, blank=True, default=None, related_name='creditee')
    seller_information = models.ForeignKey('SellerInformationProxy', null=True)
    payment_account = models.OneToOneField('PaymentAccountProxy')

    # Static labels
    sold_by_label = models.CharField(max_length=62, null=True)
    customer_reference_label = models.CharField(max_length=128, null=True)

    # Store values, since they are slow to calculate. Also, this allows for better queries
    vat = models.DecimalField(max_digits=10, decimal_places=2, default=0.)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.)
    allocated = models.DecimalField(max_digits=10, decimal_places=2, default=0.)
    due_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.)
    due_date = models.DateField(default=None, null=True)
    significant_id = models.IntegerField(default=0, null=True)
    significant_date = models.DateField(default=None, null=True)

    objects = managers.DefaultSelectOrPrefetchManager.from_queryset(managers.DocumentQuerySet)(
        select_related=(
            'quote_number',
            'invoice_number',

            'customer', 'customer__original',
            'customer__original__discount_policy',

            'end_customer', 'end_customer__original',

            'customer_address', 'customer_address__original',
            'billing_address', 'billing_address__original',
            'shipping_address', 'shipping_address__original',
            'contact', 'contact__original',
            'sold_by', 'currency',
        ),
        prefetch_related=('iteminv_set', 'iteminv_set__item', 'iteminv_set__item__product')
    )

    def get_invalid_accounts(self):
        """
        If a document has invalid agreements linked to the accounts
        :return:
        """
        items = Item.objects.on_invoice(self)
        mains = Maintenance.objects.on_invoice(self)
        citems = CustomItem.objects.on_invoice(self)

        accounts = [citem.account for citem in citems] + \
                   [item.account for item in items] + \
                   [main.serial.account for main in mains]

        inv_acc = []

        for acc in accounts:
            if not validate_account_agreement_status(acc):
                inv_acc.append(acc)

        return inv_acc if inv_acc else None

    def get_type(self):
        if self.type == self.TYPE_INVOICE:
            return "Invoice"
        if self.type == self.TYPE_DRAFT:
            return "Draft"
        return "Quote"

    def save(self, *args, suppress_labels=False, **kwargs):
        if self.pk is None and not suppress_labels:
            self.refresh_static_labels()
        super().save(*args, **kwargs)

    def refresh_static_labels(self):
        self.sold_by_label = self.sold_by.get_full_name() or self.sold_by.get_short_name()

    def refresh_values(self):
        # Refresh self.vat
        vat_sum = Decimal('0.00')
        subtotal = Decimal('0.00')

        rows = services.get_invoice_product_rows(self)
        itemrows = rows['itemrows']
        mainrows = rows['mainrows']
        citemrows = rows['citemrows']

        for row in itemrows:
            row_value = row['rowtotal']
            subtotal += row_value
            vat_rate = row['objs'][0].vat_rate
            if vat_rate:
                vat_sum += (row_value * Decimal(str(vat_rate / 100))).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)

        for row in mainrows:
            row_value = row['rowtotal']
            subtotal += row_value
            vat_rate = row['objs'][0].vat_rate
            if vat_rate:
                vat_sum += (row_value * Decimal(str(vat_rate / 100))).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)

        for row in citemrows:
            row_value = row['rowtotal']
            subtotal += row_value
            vat_rate = row['obj'].vat_rate
            if vat_rate:
                vat_sum += (row_value * Decimal(str(vat_rate / 100))).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)

        self.vat = vat_sum
        self.subtotal = subtotal
        self.total = self.subtotal + self.vat
        allocated_sum = self.allocations.aggregate(models.Sum('amount'))['amount__sum']
        if allocated_sum is None:
            self.allocated = 0
        else:
            self.allocated = allocated_sum
        self.due_amount = self.total - self.allocated

        self.due_date = self._due_date()
        self.significant_date = self._significant_date()
        self.significant_id = self._significant_id()

    def get_pdf_url(self):
        return reverse('invoice_pdf', args=[self.customer.original.pk, self.pk])

    def get_verbose_type(self):
        if self.type == Invoice.TYPE_INVOICE:
            return "Invoice"
        elif self.type == Invoice.TYPE_DRAFT:
            return "Draft"
        return "Quote"

    def _due_date(self):
        delta = datetime.timedelta(days=self.credit_period.days)
        if self.invoice_date is not None:
            return self.invoice_date + delta
        else:
            return self.quote_date + delta

    @property
    def draft_date(self):
        return self.created_at.date()

    def _significant_date(self):
        if self.is_draft:
            return self.draft_date
        elif self.is_quote:
            return self.quote_date
        elif self.is_invoice:
            return self.invoice_date

    def _significant_id(self):
        try:
            if self.is_draft:
                return self.pk
            elif self.is_quote:
                return self.quote_number.pk
            elif self.is_invoice:
                return self.invoice_number.pk
        except AttributeError:
            return 0

    def is_overdue(self):
        return self.overdue

    def is_paid(self):
        return self.due_amount == 0

    @property
    def overdue(self):
        return self.due_date < now().date()

    @property
    def allocation_rate(self):
        if self.total == 0:
            return 0
        return self.allocated / self.total

    def __str__(self):
        return self.identifier

    @property
    def identifier(self):
        if self.type == 'd':
            return u"DRA-{}".format(self.significant_id)
        elif self.type == 'q':
            return u"QUO-{}".format(self.significant_id)
        else:
            return u"INV-{}".format(self.significant_id)

    def get_absolute_url(self):
        """
        Returns the URL that points to the page representing this object
        """
        return reverse('invoice_detail', args=[self.customer.original.pk, self.pk])

    @property
    def is_draft(self):
        return services.document_is_draft(self)

    @property
    def is_quote(self):
        return services.document_is_quote(self)

    @property
    def is_invoice(self):
        return services.document_is_invoice(self)

    @property
    def get_date(self):
        # Sets the latest hour possible so Account Payment Summary will always sort invoices later than payments
        return datetime.datetime(self.invoice_date.year, self.invoice_date.month, self.invoice_date.day, 0, 0, 0)

    @property
    def get_total(self):
        return self.total


class Agreement(managers.Model):
    """
    Stores metadata for a agreement document, along with the possibility to
    store the agreement in a file
    """

    STATUS_ACTIVE = "Active"
    STATUS_TERMINATED = "Terminated"
    STATUS_EXPIRED = "Expired"

    title = models.CharField(max_length=60)
    effective_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    termination_date = models.DateTimeField(blank=True, null=True)
    summary = models.TextField(null=True, blank=True)
    customers = models.ManyToManyField('Customer', blank=True, related_name='agreements')
    file = models.OneToOneField(File, related_name='agreement')
    keywords = models.ManyToManyField(Keyword, blank=True)
    user = models.ForeignKey(User, blank=True, null=True)

    objects = managers.DefaultSelectOrPrefetchManager.from_queryset(managers.AgreementQuerySet)(
        prefetch_related=(
            'customers', 'keywords', 'accounts',
            'accounts__customer',
            'accounts__main_contact',
            'accounts__main_contact__customer',
            'accounts__agreement',
        )
    )

    class Meta:
        ordering = ('-pk',)

    def save(self, *args, **kwargs):
        new = self.pk is None
        if new:
            self.file = File.objects.create(
                label="%s documents" % str(self)
            )
        super(Agreement, self).save(*args, **kwargs)
        if new:
            # Reset the label of the file, since this agreement did not have
            # a pk before
            file_ = self.file
            file_.label = "%s documents" % str(self.identifier)
            file_.save()

    def __str__(self):
        return '{}, {}'.format(self.identifier, self.title)

    def status(self):
        if self.expiry_date and self.expiry_date <= now().date():
            return self.STATUS_EXPIRED
        if self.termination_date:
            return self.STATUS_TERMINATED
        return self.STATUS_ACTIVE

    @property
    def identifier(self):
        return "AGR-{}".format(self.pk)

    @property
    def is_valid(self):
        """
        Checks whether an agreement is valid.
        :return:
        """
        # Agreement termination date does not exist and if expiry date exists, date is > than today (not expired)
        return not bool(self.termination_date) and not (self.expiry_date and not self.expiry_date > now().date())

    @property
    def is_terminated(self):
        return bool(self.termination_date)

    @property
    def is_expired(self):
        return self.expiry_date < now().date()

    def get_absolute_url(self):
        """
        Returns the URL that points to the page representing this object
        """
        return reverse('agreement_detail', args=[self.pk])


class AgreementNote(managers.Model):
    date = models.DateField()
    content = models.TextField()
    agreement = models.ForeignKey(Agreement, related_name='notes')

    class Meta:
        ordering = ('-date', '-updated_at')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.content_rendered = markdown.markdown(self.content)

    def get_absolute_url(self):
        return self.agreement.get_absolute_url()

    def __str__(self):
        return u'note-%s' % self.pk


class MigrationSerial(managers.Model):
    """
    Many to many relation table between Customer and Migration.
    This overrides django's m2m table, adding the possibility to have one or more fields in the relation
    """
    serial = models.ForeignKey(Item)
    migration = models.ManyToManyField('Migration', related_name="migration_serials")
    previous_account = models.ForeignKey(Account, related_name="previous_account")


class Migration(managers.Model):
    """
    Stores migration of licenses across accounts
    """

    STATUS_ACTIVE = "Active"
    STATUS_DISABLED = "Disabled"

    to_account = models.ForeignKey(Account)
    from_accounts = models.ManyToManyField(Account, related_name="from_accounts")
    user = models.ForeignKey(User)

    objects = managers.DefaultSelectOrPrefetchManager.from_queryset(managers.MigrationQuerySet)()

    def __str__(self):
        return 'MIG-{}'.format(self.pk)

    def status(self):
        return self.STATUS_ACTIVE if not self.disabled else self.STATUS_DISABLED

    @property
    def identifier(self):
        return self.__str__()

    def get_absolute_url(self):
        return reverse('migration_detail', args=[self.pk])


class Import(managers.Model):
    """
    Stores data about an import of licenses from the old invoice system.
    Items and Maintenances are stored here, and creator and dates are stored
    in its superclass BaseModel, MModel. As any given Import is bound to a customer,
    a reference to customer is also stored here
    """

    STATUS_ACTIVE = "Active"
    STATUS_DISABLED = "Disabled"

    class Meta:
        ordering = ('-created_at',)

    disabled = models.BooleanField(default=False)
    customer = models.ForeignKey('Customer')
    user = models.ForeignKey(User, blank=True, null=True)
    items = models.ManyToManyField('Item', related_name='importItems')
    keywords = models.ManyToManyField('Keyword', related_name='import_set', blank=True)
    maintenance_expiry = models.DateTimeField()
    maintenance_start = models.DateTimeField(blank=True, null=True)

    objects = managers.DefaultSelectOrPrefetchManager.from_queryset(managers.ImportQuerySet)(
        select_related=('customer',),
        prefetch_related=('keywords',)
    )

    def __str__(self):
        return 'IMP-{}'.format(self.pk)

    @property
    def identifier(self):
        return self.__str__()

    @property
    def status(self):
        return self.STATUS_ACTIVE if not self.disabled else self.STATUS_DISABLED

    def get_maintenance_start(self):
        start_date = self.maintenance_expiry if self.maintenance_expiry < self.created_at else self.created_at
        return self.maintenance_start or start_date

    def get_maintenance_expiry(self):
        return self.maintenance_expiry

    @property
    def simple_import_date(self):
        return self.created_at.strftime("%Y-%m-%d")

    def collapsed_items(self):
        return collapse_list([item for item in self.items.all()])

    def get_update_url(self):
        return reverse('license_import_update', args=[self.customer.pk, self.pk])

    def get_disable_url(self):
        return reverse('license_import_disable', args=[self.customer.pk, self.pk])

    def get_absolute_url(self):
        return reverse('import_detail', args=[self.pk])


class AccountVerification(managers.Model):
    """
    This class represents a timeline for performed verifications in accounts.
     If we want to know when was the last time we ran an "Expiring maintenance" check in an account, it should be here.
    """
    EXPIRING_LICENSE_TYPE = 'EPL'
    EXPIRING_INVOICE_TYPE = 'EPI'

    VERIFICATION_TYPE_CHOICES = (
        (EXPIRING_LICENSE_TYPE, 'Expiring Licenses'),
        (EXPIRING_INVOICE_TYPE, 'Expiring Invoices'),
    )

    type = models.CharField(choices=VERIFICATION_TYPE_CHOICES, max_length=3)
    account = models.ManyToManyField(Account, related_name='verifications')

    objects = managers.DefaultSelectOrPrefetchManager.from_queryset(managers.AccountVerificationSet)()

    def __str__(self):
        return self.identifier

    def get_date(self, simple=True):
        if simple:
            return self.created_at.date()
        return self.created_at

    @property
    def identifier(self):
        return 'VER-{}'.format(self.pk)


class Task(managers.Model):
    OPEN_STATUS = '0'
    PENDING_STATUS = '1'
    CLOSED_STATUS = '2'
    STATUS_CHOICES = (
        (OPEN_STATUS, 'Open'),
        (PENDING_STATUS, 'Pending'),
        (CLOSED_STATUS, 'Closed'),
    )

    LOW_PRIORITY = 'ZLO'
    MEDIUM_PRIORITY = 'MED'
    HIGH_PRIORITY = 'AHI'
    PRIORITY = (
        (LOW_PRIORITY, 'Low'),
        (MEDIUM_PRIORITY, 'Medium'),
        (HIGH_PRIORITY, 'High'),
    )

    OVERDUE_INVOICE_TYPE = 'OIT'
    EXPIRING_LICENSE_TYPE = 'ELT'

    TASK_TYPE = (
        (OVERDUE_INVOICE_TYPE, 'Overdue Invoice'),
        (EXPIRING_LICENSE_TYPE, 'Overdue Invoice'),
    )

    deadline = models.DateField()
    title = models.CharField(max_length=120, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    agent = models.ForeignKey(User, blank=True, null=True, related_name='agent_tasks')
    keywords = models.ManyToManyField('Keyword', blank=True, related_name='event_set')
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=OPEN_STATUS)
    priority = models.CharField(max_length=3, choices=PRIORITY, null=True, blank=True)
    status_changed_at = models.DateTimeField(auto_now_add=True)
    invoices = models.ManyToManyField('Invoice')
    licenses = models.ManyToManyField('Item')
    type = models.CharField(max_length=3, choices=TASK_TYPE, null=True, blank=True)
    automatically_closed = models.BooleanField(default=False)
    factory = models.ForeignKey('TaskFactory', null=True)

    objects = managers.DefaultSelectOrPrefetchManager.from_queryset(managers.TaskQuerySet)()

    def __str__(self):
        if self.title:
            return self.title
        if self.description:
            return self.description[:15]
        else:
            return 'No name'

    @property
    def decorated_priority(self):
        if self.priority == self.LOW_PRIORITY:
            color = 'label label-success'
        elif self.priority == self.MEDIUM_PRIORITY:
            color = 'label label-warning'
        elif self.priority == self.HIGH_PRIORITY:
            color = 'label label-danger'
        else:
            return None
        return "<span class='%s'>%s</span>" % (color, self.get_priority_display())

    @property
    def done(self):
        return self.status == self.CLOSED_STATUS

    @property
    def identifier(self):
        return 'TAS-{}'.format(self.pk)

    @property
    def decorated_description(self):
        return services.decorate_with_links(self.description)

    @property
    def decorated_deadline(self):
        today = services.now().date()
        if today == self.deadline:
            color = 'attention-mark warning'
        elif today > self.deadline:
            color = 'attention-mark danger'
        else:
            color = 'attention-mark success'
        return "%s <strong class='%s'>*</strong>" % (self.deadline, color)

    @property
    def decorated_title(self):
        return services.decorate_with_links(self.title)

    def get_update_url(self):
        return reverse('task_update', args=[self.pk])

    def get_absolute_url(self):
        return reverse('task_detail', args=[self.pk])

    def assign_task(self, user):
        try:
            self.agent = user
            self.save()
        except Exception:
            raise


class TaskFactory(managers.Model):

    STATUS_ENABLED = 'Enabled'
    STATUS_DISABLED = 'Disabled'

    year_interval = models.IntegerField(default=0)
    month_interval = models.IntegerField(default=0, help_text='Must be less or equals to 12.', validators=[less_than_twelve_validator])
    day_interval = models.IntegerField(default=0)
    title = models.CharField(max_length=120, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    first_date = models.DateField()
    next_date = models.DateField()
    keywords = models.ManyToManyField('Keyword', related_name='task_factory_set', blank=True)
    task_priority = models.CharField(
        max_length=3,
        choices=Task.PRIORITY,
        null=True,
        blank=True,
        verbose_name="Tasks priority",
    )
    disabled = models.BooleanField(default=False)
    user = models.ForeignKey(User, blank=True, null=True)

    @property
    def recurrence(self):
        return '%dY, %dM, %dD' % (self.year_interval, self.month_interval, self.day_interval)

    @property
    def status(self):
        if self.disabled:
            return self.STATUS_DISABLED
        return self.STATUS_ENABLED

    @property
    def decorated_priority(self):
        if self.task_priority == Task.LOW_PRIORITY:
            color = 'label label-success'
        elif self.task_priority == Task.MEDIUM_PRIORITY:
            color = 'label label-warning'
        elif self.task_priority == Task.HIGH_PRIORITY:
            color = 'label label-danger'
        else:
            return None
        return "<span class='%s'>%s</span>" % (color, self.get_task_priority_display())

    @property
    def decorated_description(self):
        return services.decorate_with_links(self.description)

    def __str__(self):
        if self.title:
            return self.title
        if self.description:
            return self.description[:15]
        else:
            return 'No name'

    @property
    def identifier(self):
        return 'FAC-{}'.format(self.pk)

    def get_absolute_url(self):
        return reverse('task_factory_detail', args=[self.pk])


class SellerInformation(managers.Model):
    """
    To store the email by which we are contacted
    """
    name = models.CharField(max_length=80)
    street1 = models.CharField(max_length=80)
    street2 = models.CharField(max_length=80, blank=True, null=True)
    zipcode = models.CharField(max_length=80)
    city = models.CharField(max_length=80)
    country = models.CharField(max_length=2, choices=constants.COUNTRIES)
    eu_vat = models.CharField(max_length=80, blank=True, null=True)
    us_ein = models.CharField(max_length=80, blank=True, null=True)
    aribaid = models.CharField(max_length=80, blank=True, null=True)
    phone = models.CharField(max_length=80)
    fax = models.CharField(max_length=80, blank=True, null=True)
    cvr = models.CharField(max_length=80)
    email = models.EmailField(max_length=80)
    remit_email = models.EmailField(max_length=80, blank=True, null=True)
    web = models.CharField(max_length=80, blank=True, null=True)

    @property
    def identifier(self):
        return 'SEL-{}'.format(self.pk)

    def __str__(self):
        return '{} {}'.format(self.identifier, self.name)


class SellerInformationProxy(managers.FlattenedProxyModel):
    original = models.ForeignKey('SellerInformation')

    name = models.CharField(max_length=80)
    street1 = models.CharField(max_length=80)
    street2 = models.CharField(max_length=80, blank=True, null=True)
    zipcode = models.CharField(max_length=80)
    city = models.CharField(max_length=80)
    country = models.CharField(max_length=2, choices=constants.COUNTRIES)
    eu_vat = models.CharField(max_length=80, blank=True, null=True)
    us_ein = models.CharField(max_length=80, blank=True, null=True)
    aribaid = models.CharField(max_length=80, blank=True, null=True)
    phone = models.CharField(max_length=80)
    fax = models.CharField(max_length=80, blank=True, null=True)
    cvr = models.CharField(max_length=80)
    email = models.EmailField(max_length=80)
    remit_email = models.EmailField(max_length=80, blank=True, null=True)
    web = models.CharField(max_length=80, blank=True, null=True)

    @property
    def identifier(self):
        return 'SIP-{}'.format(self.pk)

    def __str__(self):
        return '{} {}'.format(self.identifier, self.name)


class Template(managers.Model):
    """
    Templates, for rendering invoices. Should be consistent at all times.
    """
    content = models.TextField()
    previous = models.ForeignKey('Template', null=True, related_name='next')

    @property
    def identifier(self):
        return 'TEM-{}'.format(self.pk)

    def __str__(self):
        return '{}'.format(self.identifier)


class CustomInvoiceLine(managers.Model):
    """
    For each customer is the option to add custom lines to its invoices. These
    are set on the customer page and if chosen, they will be displayed on
    invoices for that customer. When the invoice is upgraded from quote to
    invoice, the user will have the option to change the values of the lines for
    that one invoice.
    """
    customer = models.ForeignKey('Customer', blank=True, null=True, related_name='custom_invoice_lines')
    invoice = models.ForeignKey('Invoice', blank=True, null=True, related_name='custom_invoice_lines')
    header = models.CharField(max_length=120)
    value = models.CharField(max_length=120, blank=True, null=True, default='')
    on_invoice = models.BooleanField(default=True)

    objects = managers.DefaultSelectOrPrefetchManager.from_queryset(managers.CustomInvoiceLineQuerySet)()

    def get_update_url(self):
        return reverse('custom_invoice_line_update', args=[self.customer.pk, self.pk])


class Report(managers.Model):
    """
    A wrapper for saving filters for a report. This model has no fields, as
    it is simply pointed to by chain objects. It does, however, have some neat
    helper functions
    """
    SALES_REPORT_TYPE = '0'
    ALLOCATION_REPORT_TYPE = '1'
    PRODUCT_REPORT_TYPE = '2'
    AGED_DEBTOR_TYPE = '3'
    LICENSE_REPORT_TYPE = '4'
    MAINTENANCE_REPORT_TYPE = '5'

    # @ IMPORTANT @
    # Remember to update the fields dictionaries down below in case a new report type is added

    TYPE_CHOICES = (
        (AGED_DEBTOR_TYPE, "Aged Debtor Report"),
        (LICENSE_REPORT_TYPE, "Account Licenses Report"),
        (MAINTENANCE_REPORT_TYPE, "Customer Maintenance Report"),
        (ALLOCATION_REPORT_TYPE, "Invoices, Payments and Allocations Report"),
        (PRODUCT_REPORT_TYPE, "Part-ID Payment Report"),
        (SALES_REPORT_TYPE, "Sales Report"),
    )

    # These variables store which fields will be used to generate the report.
    # This is used in the forms.py file to prevent unnecessary fields from being generated in the template

    SALES_REPORT_FIELDS = [
        'type',
        'start_date',
        'end_date',
        'currencies',
        'products',
        'include_products',
        'include_maintenance',
        'include_reverses',
        'customers',
    ]

    ALLOCATION_REPORT_FIELDS = [
        'type',
        'start_date',
        'end_date',
        'currencies',
        'include_reverses',
        'customers',
    ]

    LICENSE_REPORT_FIELDS = [
        'type',
        'start_date',
        'end_date',
        'customers',
        'include_details'
    ]

    PRODUCT_REPORT_FIELDS = [
        'type',
        'start_date',
        'end_date',
        'currencies',
        'products',
        'include_reverses',
    ]

    AGED_DEBTOR_REPORT_FIELDS = [
        'type',
        'start_date',
        'end_date',
    ]

    MAINTENANCE_REPORT_FIELDS = [
        'type',
        'start_date',
        'end_date',
    ]

    # @ IMPORTANT @
    # Report types. The KEY is the code and the content, the fields.
    # If a new report is included, this needs to be updated
    REPORT_TYPES = {
        SALES_REPORT_TYPE: SALES_REPORT_FIELDS,
        ALLOCATION_REPORT_TYPE: ALLOCATION_REPORT_FIELDS,
        PRODUCT_REPORT_TYPE: PRODUCT_REPORT_FIELDS,
        AGED_DEBTOR_TYPE: AGED_DEBTOR_REPORT_FIELDS,
        LICENSE_REPORT_TYPE: LICENSE_REPORT_FIELDS,
        MAINTENANCE_REPORT_TYPE: MAINTENANCE_REPORT_FIELDS,
    }

    name = models.CharField(max_length=128, blank=True)
    type = models.CharField(max_length=1, choices=TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    currencies = models.ManyToManyField(Currency, blank=True, related_name='currencies')
    invoices = models.ManyToManyField(Invoice, blank=True, related_name='invoices')
    products = models.ManyToManyField(Product, blank=True, related_name='products')
    serials = models.ManyToManyField(Item, blank=True, related_name='serials')
    include_products = models.BooleanField(default=True, verbose_name='Include products')
    include_maintenance = models.BooleanField(default=True, verbose_name='Include maintenance')
    include_reverses = models.BooleanField(default=True, verbose_name='Include reversed')
    customers = models.ManyToManyField('Customer', blank=True, related_name='customers')
    author = models.ForeignKey(User)
    private = models.BooleanField(default=False)

    objects = managers.DefaultSelectOrPrefetchManager.from_queryset(managers.ReportQuerySet)(
        select_related=('author', ),
        prefetch_related=('currencies', 'products', 'customers')
    )

    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return u'%s' % str(self.name)

    @property
    def identifier(self):
        return "REP-%s" % self.id

    def get_absolute_url(self):
        return reverse('report_detail', args=[self.pk])

    def verbose_type(self):
        for k, v in self.TYPE_CHOICES:
            if k == self.type:
                return v

    def get_invoices(self):
        products = self.get_products()
        customers = self.get_customers()
        currencies = self.get_currencies()
        return Invoice.objects.filter(
            type='i',
            currency__in=currencies,
            end_customer__original__in=customers
        ).distinct().filter(
            models.Q(iteminv__item__product__in=products) |
            models.Q(maintenances__serial__product__in=products) |
            models.Q(citems__assocs__product__in=products)
        ).distinct()

    def get_products(self):
        return self.products.all() if self.products.exists() else Product.objects.all()

    def get_customers(self):
        return self.customers.all() if self.customers.exists() else Customer.objects.all()

    def get_currencies(self):
        return self.currencies.all() if self.currencies.exists() else Currency.objects.all()


class VatCheck(managers.Model):
    country_code = models.TextField()
    number = models.TextField()
    date_string = models.DateTimeField()
    company_name = models.TextField()
    address = models.TextField()
    token = models.TextField()
    valid = models.BooleanField()

    objects = managers.DefaultSelectOrPrefetchManager.from_queryset(managers.VatCheckQuerySet)()

    class Meta:
        ordering = ('-pk', )

    def __str__(self):
        return u'%s' % str(self.id)

    def identifier(self):
        return u'VAL-%s' % self

    def is_valid(self):
        return self.token != ''

    def as_dict(self):
        return dict(
            country_code=self.country_code,
            number=self.number,
            date_string=str(self.date_string),
            company_name=self.company_name,
            address=self.address,
            token=self.token,
        )


class ZendeskToken(managers.Model):
    user = models.ForeignKey(User, related_name='tokens')
    email = models.EmailField()
    token = models.CharField(max_length=40)


class TemplateVariable(managers.Model):
    name = models.CharField(max_length=32, unique=True)
    text = models.TextField()
    author = models.ForeignKey(User)
    private = models.BooleanField(default=False, help_text="The variable can only be used by the user creating it.")

    objects = managers.DefaultSelectOrPrefetchManager.from_queryset(managers.TemplateVariableQuerySet)()

    class Meta:
        unique_together = (('name', 'author'),)


class Message(managers.Model):
    author = models.ForeignKey(User, null=True)
    content = models.TextField()
    anchored = models.BooleanField(default=False)

    # Auto generated
    html = models.TextField()

    objects = managers.DefaultSelectOrPrefetchManager.from_queryset(managers.MessageQuerySet)()

    class Meta:
        ordering = ('-pk',)

    def identifier(self):
        return "MSG-{}".format(self.id)

    def __str__(self):
        return "MSG-{}".format(self.id)

    def save(self, *args, **kwargs):
        self.html = services.decorate_with_links(self.content)
        return super(Message, self).save(*args, **kwargs)

    def get_author(self):
        return self.author if self.author else 'System'

    def get_html_content(self):
        return self.html


class EmailTemplate(managers.Model):
    name = models.CharField(max_length=120, unique=True)
    subject = models.CharField(null=True, blank=True, max_length=100)
    content = models.TextField()
    types = models.TextField()
    auto_account_summary_default = models.BooleanField(default=False)

    rendered_plain = ""
    rendered_html = ""

    MAIL_DOCUMENT = 'doc_mail'
    ZENDESK_DOCUMENT = 'doc_zendesk'
    MAIL_SUMMARY = 'act_mail'
    ZENDESK_SUMMARY = 'act_zendesk'
    MAIL_PAY_SUMMARY = 'pay_mail'
    ZENDESK_PAY_SUMMARY = 'pay_zendesk'

    AVAILABLE_TYPES = [
        (MAIL_DOCUMENT, 'E-mail'),
        (ZENDESK_DOCUMENT, 'Zendesk Ticket'),
        (MAIL_SUMMARY, 'Email Account Summary'),
        (ZENDESK_SUMMARY, 'Zendesk Account Summary'),
        (MAIL_PAY_SUMMARY, 'Email Payments Summary'),
        (ZENDESK_PAY_SUMMARY, 'Zendesk Payments Summary'),
    ]

    def __str__(self):
        return self.name

    def render(self, user, context=None, target=None):
        context = context or EmailTemplate.get_context(user, target)
        tpl = MarkdownTemplate(self.content)
        tpl.render(context)
        self.rendered_plain = tpl.plain
        self.rendered_html = tpl.html

    @staticmethod
    def get_context(user, target=None):
        """
        Gets a context dictionary to use for rendering the template. If no
        target is given, the dict is populated with placeholder values. If a
        target is given, the dictionary is populated with relevant data from
        that target, e.g. if you provide an invoice as target, the 'invoice_id'
        will be set to the id of the invoice instead of 'INV-XX'.

        A user needs to be specified, so that the accessible variables can be
        retrieved and appended to the context as well.
        """
        def set_value(target, target_lookup, default):
            if target is None:
                return default
            for classname, field in target_lookup:
                if isinstance(target, classname):
                    parts = field.split('.')
                    val = target
                    for part in parts:
                        if part == '__s__':
                            val = SellerInformation.objects.first()
                            continue
                        try:
                            val = getattr(val, part)
                        except AttributeError:
                            return ''
                    return val

                    return getattr(target, field, '')
            return ''

        context = OrderedDict([
            ('account_id', set_value(
                target,
                [(Account, 'identifier')],
                'ACT-XX'
            )),
            ('invoice_id', set_value(
                target,
                [(Invoice, 'identifier')],
                'INV-XX'
            )),
            ('your_reference', set_value(
                target,
                [(Invoice, 'customer_reference_label')],
                'PO123456'
            )),
            ('contact_name', set_value(
                target,
                [
                    (Invoice, 'contact.fullname'),
                    (Account, 'main_contact.fullname'),
                ],
                'John w. Smith'
            )),
            ('contact_first_name', set_value(
                target,
                [
                    (Invoice, 'contact.first_name'),
                    (Account, 'main_contact.first_name'),
                ],
                'John'
            )),
            ('contact_last_name', set_value(
                target,
                [
                    (Invoice, 'contact.last_name'),
                    (Account, 'main_contact.last_name'),
                ],
                'Smith'
            )),
            ('contact_email', set_value(
                target,
                [
                    (Invoice, 'contact.email'),
                    (Account, 'main_contact.email'),
                ],
                'john@example.com'
            )),
            ('seller_name', set_value(
                target,
                [
                    (Invoice, 'seller_information.name'),
                    (Account, '__s__.name'),
                ],
                'Company Name'
            )),
            ('seller_street1', set_value(
                target,
                [
                    (Invoice, 'seller_information.street1'),
                    (Account, '__s__.street1'),
                ],
                'Street1'
            )),
            ('seller_street2', set_value(
                target,
                [
                    (Invoice, 'seller_information.street2'),
                    (Account, '__s__.street2'),
                ],
                'Street2'
            )),
            ('seller_zipcode', set_value(
                target,
                [
                    (Invoice, 'seller_information.zipcode'),
                    (Account, '__s__.zipcode'),
                ],
                '1234'
            )),
            ('seller_city', set_value(
                target,
                [
                    (Invoice, 'seller_information.city'),
                    (Account, '__s__.city'),
                ],
                'City'
            )),
            ('seller_country', set_value(
                target,
                [
                    (Invoice, 'seller_information.country'),
                    (Account, '__s__.country'),
                ],
                'Denmark'
            )),
            ('seller_eu_vat', set_value(
                target,
                [
                    (Invoice, 'seller_information.eu_vat'),
                    (Account, '__s__.eu_vat'),
                ],
                'DK1234567'
            )),
            ('seller_us_ein', set_value(
                target,
                [
                    (Invoice, 'seller_information.us_ein'),
                    (Account, '__s__.us_ein'),
                ],
                '123123123'
            )),
            ('seller_aribaid', set_value(
                target,
                [
                    (Invoice, 'seller_information.aribaid'),
                    (Account, '__s__.aribaid'),
                ],
                '321321321'
            )),
            ('seller_phone', set_value(
                target,
                [
                    (Invoice, 'seller_information.phone'),
                    (Account, '__s__.phone'),
                ],
                '88888888'
            )),
            ('seller_fax', set_value(
                target,
                [
                    (Invoice, 'seller_information.fax'),
                    (Account, '__s__.fax'),
                ],
                '99999999'
            )),
            ('seller_cvr', set_value(
                target,
                [
                    (Invoice, 'seller_information.cvr'),
                    (Account, '__s__.cvr'),
                ],
                '2121212121'
            )),
            ('seller_email', set_value(
                target,
                [
                    (Invoice, 'seller_information.email'),
                    (Account, '__s__.email'),
                ],
                'foo@example.com'
            )),
            ('seller_remit_email', set_value(
                target,
                [
                    (Invoice, 'seller_information.remit_email'),
                    (Account, '__s__.remit_email'),
                ],
                'foo@example.com'
            )),
            ('seller_web', set_value(
                target,
                [
                    (Invoice, 'seller_information.web'),
                    (Account, '__s__.web'),
                ],
                'www.example.com'
            )),
        ])
        variables = TemplateVariable.objects.available_to_user(
            user
        ) | TemplateVariable.objects.public()
        for var in variables:
            context[var.name] = var.text
        return context

    @property
    def allowed_types(self):
        return self.types.split(',')

    @property
    def allowed_types_display(self):
        display = []
        for t in self.allowed_types:
            for a in self.AVAILABLE_TYPES:
                if t == a[0]:
                    display.append(a[1])
        return display


class Communication(managers.Model):
    """
    Represents a communication.py (e-mails and tickets sent through Zendesk integration) between the user and the customer.
    The idea is to generate a log of all dispatched documents to a certain customer and its contacts for further
    consultation
    """
    TYPE_ZENDESK_TICKET = 'TZT'
    TYPE_EMAIL_MESSAGE = 'TEM'

    COMMUNICATION_TYPE = (
        (TYPE_ZENDESK_TICKET, 'Zendesk Ticket'),
        (TYPE_EMAIL_MESSAGE, 'E-mail')
    )

    subject = models.CharField(max_length=500, null=True, blank=True)
    recipient = models.CharField(max_length=50, null=True, blank=True)
    cc = models.CharField(max_length=200, null=True, blank=True)
    content = models.CharField(max_length=2000)
    type = models.CharField(choices=COMMUNICATION_TYPE, max_length=3)
    customer = models.ForeignKey(Customer)
    ticket_nr = models.CharField(max_length=20, null=True, blank=True)
    document = models.ForeignKey(Invoice, null=True, blank=True)
    user = models.ForeignKey(User, null=True, blank=True)

    class Meta:
        ordering = ('-pk',)

    @property
    def identifier(self):
        return "COM-{}".format(self.pk)

    def __str__(self):
        return "%s" % self.identifier

    def get_absolute_url(self):
        return reverse('communication_detail', args=[self.pk])

    def get_zendesk_url(self):
        return 'www.importantinformation.com' % self.ticket_nr

    def get_document_url(self):
        return self.document.get_absolute_url() if self.document else None


class UserHistory(managers.Model):
    """
    Class used to save user's visited pages.
    """
    user = models.ForeignKey(User)
    page_name = models.CharField(max_length=200)
    url = models.URLField()

    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return 'HIS-{}'.format(self.pk)

    @property
    def label(self):
        return self.page_name

    def get_absolute_url(self):
        return self.url
