from sqlalchemy import Index, Numeric, func, text

from .services.database import db


class User(db.Model):
    __tablename__ = "user"
    __table_args__ = (
        Index("uq_user_email_ci", text("lower(email)"), unique=True),
        Index("uq_user_name_ci", text("lower(name)"), unique=True),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())


class Product(db.Model):
    __tablename__ = "product"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    marca = db.Column(db.String(255), nullable=False)
    valor = db.Column(Numeric(12, 2), nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
