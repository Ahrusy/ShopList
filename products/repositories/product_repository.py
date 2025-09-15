from ..models import Product, Category, Shop, Tag, ProductImage

class ProductRepository:
    @staticmethod
    def get_all_products():
        return Product.objects.all().prefetch_related('images', 'category', 'shops', 'tags')

    @staticmethod
    def get_product_by_id(product_id):
        return Product.objects.get(pk=product_id)

    @staticmethod
    def create_product(data):
        product = Product.objects.create(**data)
        return product

    @staticmethod
    def update_product(product_id, data):
        product = Product.objects.get(pk=product_id)
        for key, value in data.items():
            setattr(product, key, value)
        product.save()
        return product

    @staticmethod
    def delete_product(product_id):
        product = Product.objects.get(pk=product_id)
        product.delete()