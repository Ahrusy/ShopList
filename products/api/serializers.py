from rest_framework import serializers
from ..models import Product, Category, Shop, Tag, ProductImage, User, Seller, ProductCharacteristic, Order, OrderItem, Review, Cart, CartItem, Commission, Location, UserLocation

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'phone_number', 'avatar', 'date_of_birth', 'address']
        read_only_fields = ['role']

class SellerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Seller
        fields = ['id', 'user', 'company_name', 'description', 'commission_rate', 'is_verified', 'rating', 'total_sales', 'total_revenue', 'created_at']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'created_at']

class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ['id', 'name', 'address', 'city', 'latitude', 'longitude', 'created_at']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class ProductCharacteristicSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCharacteristic
        fields = ['id', 'name', 'value', 'unit', 'order']

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'order']

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category', write_only=True)
    seller = SellerSerializer(read_only=True)
    seller_id = serializers.PrimaryKeyRelatedField(queryset=Seller.objects.all(), source='seller', write_only=True)
    shops = ShopSerializer(many=True, read_only=True)
    shop_ids = serializers.PrimaryKeyRelatedField(queryset=Shop.objects.all(), many=True, source='shops', write_only=True)
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True, source='tags', write_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    characteristics = ProductCharacteristicSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'discount_price', 'currency',
            'category', 'category_id', 'seller', 'seller_id', 'shops', 'shop_ids', 
            'tags', 'tag_ids', 'images', 'characteristics', 'created_at', 'updated_at',
            'views_count', 'rating', 'reviews_count', 'is_active', 'stock_quantity', 'sku'
        ]
        read_only_fields = ['created_at', 'updated_at', 'views_count', 'rating', 'reviews_count', 'sku']

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source='product', write_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_id', 'quantity', 'price', 'total_price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'status', 'payment_status', 'total_amount',
            'shipping_cost', 'discount_amount', 'shipping_address', 'notes',
            'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['order_number', 'created_at', 'updated_at']

class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    product = ProductSerializer(read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'id', 'user', 'product', 'order', 'rating', 'title', 'text',
            'is_verified_purchase', 'is_moderated', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source='product', write_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'created_at']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class CommissionSerializer(serializers.ModelSerializer):
    seller = SellerSerializer(read_only=True)
    order = OrderSerializer(read_only=True)
    
    class Meta:
        model = Commission
        fields = ['id', 'seller', 'order', 'amount', 'rate', 'created_at']
        read_only_fields = ['created_at']


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'name', 'region', 'country', 'latitude', 'longitude', 'is_active', 'created_at']
        read_only_fields = ['created_at']


class UserLocationSerializer(serializers.ModelSerializer):
    location = LocationSerializer(read_only=True)
    location_id = serializers.PrimaryKeyRelatedField(queryset=Location.objects.filter(is_active=True), source='location', write_only=True)
    
    class Meta:
        model = UserLocation
        fields = ['id', 'location', 'location_id', 'is_auto_detected', 'created_at']
        read_only_fields = ['created_at']