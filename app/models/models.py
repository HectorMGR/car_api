from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, Boolean, Numeric, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="admin", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"


class Brand(Base):
    __tablename__ = "brands"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    # Relationships
    models: Mapped[list["Model"]] = relationship(back_populates="brand", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Brand(id={self.id}, name='{self.name}')>"


class Model(Base):
    __tablename__ = "models"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    brand_id: Mapped[int] = mapped_column(ForeignKey("brands.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Relationships
    brand: Mapped["Brand"] = relationship(back_populates="models")
    vehicles: Mapped[list["Vehicle"]] = relationship(back_populates="model", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Model(id={self.id}, name='{self.name}')>"


class Currency(Base):
    __tablename__ = "currencies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(3), unique=True, nullable=False)
    symbol: Mapped[str] = mapped_column(String(5), nullable=False)

    # Relationships
    vehicles: Mapped[list["Vehicle"]] = relationship(back_populates="currency")

    def __repr__(self) -> str:
        return f"<Currency(id={self.id}, code='{self.code}')>"


class VehicleStatus(Base):
    __tablename__ = "vehicle_status"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    # Relationships
    vehicles: Mapped[list["Vehicle"]] = relationship(back_populates="status")

    def __repr__(self) -> str:
        return f"<VehicleStatus(id={self.id}, name='{self.name}')>"


class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    model_id: Mapped[int] = mapped_column(ForeignKey("models.id"), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    currency_id: Mapped[int] = mapped_column(ForeignKey("currencies.id"), nullable=False)
    status_id: Mapped[int] = mapped_column(ForeignKey("vehicle_status.id"), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    model: Mapped["Model"] = relationship(back_populates="vehicles")
    currency: Mapped["Currency"] = relationship(back_populates="vehicles")
    status: Mapped["VehicleStatus"] = relationship(back_populates="vehicles")
    images: Mapped[list["VehicleImage"]] = relationship(back_populates="vehicle", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Vehicle(id={self.id}, year={self.year}, price={self.price})>"


class VehicleImage(Base):
    __tablename__ = "vehicle_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    vehicle: Mapped["Vehicle"] = relationship(back_populates="images")

    def __repr__(self) -> str:
        return f"<VehicleImage(id={self.id}, is_primary={self.is_primary})>"
