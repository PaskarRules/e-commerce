from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

# from .views import make_thumbnail

# Create your models here.

class Customer(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, null=True)
    email = models.EmailField(max_length=50)
    phone = models.CharField(max_length=50, null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField()
    parent = models.ForeignKey('self', blank=True, null=True, related_name='children', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('slug', 'parent',)
        verbose_name_plural = "categories"

    def get_absolute_url(self):
        return reverse('category', args=[self.slug])

    def get_breadcrumb(self):
        full_path = [(self.name, self.get_absolute_url())]
        k = self.parent
        while k is not None:
            full_path.append((k.name, k.get_absolute_url()))
            k = k.parent
        full_path.reverse()
        return full_path

    def __str__(self):
        full_path = [self.name]
        k = self.parent
        while k is not None:
            full_path.append(k.name)
            k = k.parent
        full_path.reverse()
        return ' -> '.join(full_path)


class Product(models.Model):
    STOCK = [
        ('In stock', 'В наявності'),
        ('Not available', 'Нема в наявності'),
    ]
    name = models.CharField(max_length=200)
    price = models.FloatField()
    brand = models.CharField(max_length=30, null=False, blank=True, default="")
    stock = models.CharField(max_length=200, null=False, default=STOCK[0][0], choices=STOCK)
    digital = models.BooleanField(default=False, null=True, blank=True)
    category = models.ManyToManyField(Category)
    image = models.ImageField(null=True)
    description = models.TextField(max_length=1700, null=False, blank=True, default="")
    composition = models.TextField(max_length=1200, null=False, blank=True, default="")

    def __str__(self):
        return self.name

    def get_stock(self):
        result = [item for item in self.STOCK if item[0] == self.stock][0][1]

        return result

    def get_product_url(self):
        return f'product/product-{self.id}/'

    def get_cat_list(self):
        k = self.category  # for now ignore this instance method

        breadcrumb = ["dummy"]
        while k is not None:
            breadcrumb.append(k.slug)
            k = k.parent
        for i in range(len(breadcrumb) - 1):
            breadcrumb[i] = '/'.join(breadcrumb[-1:i - 1:-1])
        return breadcrumb[-1:0:-1]

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url


class Order(models.Model):
    STATUS = [
        ('Cart_order', 'Cart_order'),
        ('Not confirmed', 'Не підтверджений'),
        ('Called', 'Підтверджений'),
        ('Payed', 'Оплачений'),
        ('Sent', 'Відправлений'),
        ('Delivered', 'Виконаний'),
        ('Canceled', 'Скасований')
    ]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=200, null=False, default=STATUS[0][0], choices=STATUS)
    transaction_id = models.CharField(max_length=100, null=True)
    total_price = models.FloatField(null=True)
    note = models.CharField(max_length=200, null=False, blank=True, default="")

    def __str__(self):
        return str(f'{self.id}, {self.customer.name}')

    def get_status(self):
        result = [item for item in self.STATUS if item[0] == self.status][0][1]

        return result

    @property
    def shipping(self):
        shipping = False
        orderitems = self.orderitem_set.all()
        for i in orderitems:
            if i.product.digital == False:
                shipping = True
        return shipping

    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(f'order {self.order.id}, {self.product}, {self.date_added}')

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total


class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    address = models.CharField(max_length=200, null=False)
    city = models.CharField(max_length=200, null=False)
    state = models.CharField(max_length=200, null=False)
    zipcode = models.CharField(max_length=200, null=False)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address
