import uuid

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm.state import InstanceState
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import (inspect, Column, String, SmallInteger, UniqueConstraint,
                        CheckConstraint, ForeignKey, Integer)

from app_creator import app


MAX_FIELD_LENGTH = 64


db = SQLAlchemy(app, engine_options={"pool_size":20, "max_overflow": 0})
Base = declarative_base()


class ImprovedBase:
    @property
    def as_dict(self):
        return {
            c.key: getattr(self, c.key)
            for c in inspect(self).mapper.column_attrs
            if not isinstance(getattr(self, c.key), InstanceState)
        }


class User(Base, ImprovedBase):
    __tablename__ = 'users'

    def __repr__(self):
        full_name = f'{self.first_name} {self.last_name}'
        if len(full_name) > MAX_FIELD_LENGTH:
            return f"<{full_name[:MAX_FIELD_LENGTH]}…>"
        return f"<{full_name}>"

    id = Column(UUID(), nullable=False, primary_key=True, default=lambda: str(uuid.uuid4()))
    first_name = Column(String(512), nullable=False)
    last_name = Column(String(512), nullable=False)
    email = Column(String(256), nullable=False, unique=True)
    password_hash = Column(String(64), nullable=False)

    feedback = relationship("Feedback", back_populates='user_ref', primaryjoin="Feedback.user_id == User.id")
    cart = relationship("CartItem", back_populates='user_ref', primaryjoin="CartItem.user_id == User.id")
    wishlist = relationship("WishListItem", back_populates='user_ref', primaryjoin="WishListItem.user_id == User.id")


class Product(Base, ImprovedBase):
    __tablename__ = 'products'

    def __repr__(self):
        if len(self.name) > MAX_FIELD_LENGTH:
            return f"<{self.name[:MAX_FIELD_LENGTH]}…>"
        return f"<{self.name}>"

    id = Column(UUID(), nullable=False, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(128), nullable=False, unique=True)
    description = Column(String(2048), nullable=False, unique=True)
    characteristics = Column(JSONB(), nullable=False)
    type = Column(UUID(), ForeignKey('product_types.id', ondelete='NO ACTION'), nullable=False)
    price = Column(Integer(), nullable=False)

    type_ref = relationship("ProductType", back_populates='products', foreign_keys=[type])

    tags = relationship("TagToProduct", back_populates='product_ref', primaryjoin="TagToProduct.product_id == Product.id")
    feedback = relationship("Feedback", back_populates='product_ref', primaryjoin="Feedback.product_id == Product.id")
    cart_occurrences = relationship("CartItem", back_populates='product_ref', primaryjoin="CartItem.product_id == Product.id")
    wishlist_occurrences = relationship("WishListItem", back_populates='product_ref',
                                        primaryjoin="WishListItem.product_id == Product.id")
    pictures = relationship("ProductPicture", back_populates='product_ref',
                            primaryjoin="ProductPicture.product_id == Product.id")


class ProductType(Base, ImprovedBase):
    __tablename__ = 'product_types'

    def __repr__(self):
        if len(self.name) > MAX_FIELD_LENGTH:
            return f"<{self.name[:MAX_FIELD_LENGTH]}…>"
        return f"<{self.name}>"

    id = Column(UUID(), nullable=False, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(128), nullable=False, unique=True)
    picture = Column(String(1024), nullable=False)

    products = relationship("Product", back_populates='type_ref', primaryjoin="ProductType.id == Product.type")


class Tag(Base, ImprovedBase):
    __tablename__ = 'tags'

    def __repr__(self):
        if len(self.title) > MAX_FIELD_LENGTH:
            return f"<{self.title[:MAX_FIELD_LENGTH]}…>"
        return f"<{self.title}>"

    id = Column(UUID(), nullable=False, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(128), nullable=False, unique=True)

    products = relationship("TagToProduct", back_populates='tag_ref', primaryjoin="Tag.id == TagToProduct.tag_id")


class TagToProduct(Base, ImprovedBase):
    __tablename__ = 'tags_to_products'

    def __repr__(self):
        result = f'{self.tag_ref.title} to {self.product_ref.name}'
        if len(result) > MAX_FIELD_LENGTH:
            return f"<{result[:MAX_FIELD_LENGTH]}…>"
        return f"<{result}>"

    id = Column(UUID(), nullable=False, primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(UUID(), ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    tag_id = Column(UUID(), ForeignKey('tags.id', ondelete='CASCADE'), nullable=False)

    product_ref = relationship("Product", back_populates='tags', foreign_keys=[product_id])
    tag_ref = relationship("Tag", back_populates='products', foreign_keys=[tag_id])


class ProductPicture(Base, ImprovedBase):
    __tablename__ = 'product_pictures'

    def __repr__(self):
        result = f'{self.product_ref.name}: {self.link}'
        if len(result) > MAX_FIELD_LENGTH:
            return f"<{result[:MAX_FIELD_LENGTH]}…>"
        return f"<{result}>"

    id = Column(UUID(), nullable=False, primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(UUID(), ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    link = Column(String(1024), nullable=False)

    product_ref = relationship("Product", back_populates='pictures', foreign_keys=[product_id])


class CartItem(Base, ImprovedBase):
    __tablename__ = 'cart_items'

    def __repr__(self):
        result = f'{self.user_ref.first_name} {self.user_ref.last_name}`s {self.product_ref.name}'
        if len(result) > MAX_FIELD_LENGTH:
            return f"<{result[:MAX_FIELD_LENGTH]}…>"
        return f"<{result}>"

    id = Column(UUID(), nullable=False, primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(UUID(), ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(UUID(), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    cart_items_user_id_product_id_key = UniqueConstraint('product_id', 'user_id', name='cart_items_user_id_product_id_key')

    product_ref = relationship("Product", back_populates='cart_occurrences', foreign_keys=[product_id])
    user_ref = relationship("User", back_populates='cart', foreign_keys=[user_id])


class WishListItem(Base, ImprovedBase):
    __tablename__ = 'wishlist'

    def __repr__(self):
        result = f'{self.user_ref.first_name} {self.user_ref.last_name}`s {self.product_ref.name}'
        if len(result) > MAX_FIELD_LENGTH:
            return f"<{result[:MAX_FIELD_LENGTH]}…>"
        return f"<{result}>"

    id = Column(UUID(), nullable=False, primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(UUID(), ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(UUID(), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    wishlist_user_id_product_id_key = UniqueConstraint('product_id', 'user_id', name='wishlist_user_id_product_id_key')

    product_ref = relationship("Product", back_populates='wishlist_occurrences', foreign_keys=[product_id])
    user_ref = relationship("User", back_populates='wishlist', foreign_keys=[user_id])


class Feedback(Base, ImprovedBase):
    __tablename__ = 'feedback'

    def __repr__(self):
        prod_name = self.product_ref.name
        prod_name = prod_name[:8] + '…' if len(prod_name) > 8 else prod_name
        user_name = self.user_ref.__repr__()
        user_name = user_name[:12] + '…' if len(user_name) > 12 else user_name
        result = f'({prod_name}) {user_name}: {self.stars}, {self.body}'
        if len(result) > MAX_FIELD_LENGTH:
            return f"<{result[:MAX_FIELD_LENGTH]}…>"
        return f"<{result}>"

    id = Column(UUID(), nullable=False, primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(UUID(), ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(UUID(), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    body = Column(String(4096), nullable=False)
    stars = Column(SmallInteger(), nullable=False)

    feedback_stars_check = CheckConstraint('(stars <= 5 AND stars >= 0)', name='feedback_stars_check')

    product_ref = relationship("Product", back_populates='feedback', foreign_keys=[product_id])
    user_ref = relationship("User", back_populates='feedback', foreign_keys=[user_id])


def fill_db_with_test_data():
    import random

    def generate_random_token(length: int) -> str:
        letters = bytes(range(b'a'[0], b'z'[0] + 1)).decode()
        symbols = list(letters + letters.upper() + "-_")
        symbols.extend(bytes(range(b'0'[0], b'9'[0] + 1)).decode())
        return str.join('', (random.choice(symbols) for _ in range(length)))

    with app.app_context():
        types = db.session.query(ProductType).all()
        for i in range(1000):
            for j in range(2000):
                new_product = Product()
                new_product.id = str(uuid.uuid4())
                new_product.price = random.randint(1, 100000)
                new_product.description = generate_random_token(100)
                new_product.name = generate_random_token(16)
                new_product.characteristics = {generate_random_token(1): generate_random_token(2)}
                new_product.type = random.choice(types).id
                db.session.add(new_product)
            db.session.commit()


#fill_db_with_test_data()
