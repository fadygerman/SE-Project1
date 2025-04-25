from fastapi import APIRouter, Body, Depends, HTTPException, Query, status as api_status
from sqlalchemy.orm import Session

from database import get_db
from exceptions.bookings import *
from exceptions.currencies import CurrencyServiceUnavailableException
from models.db_models import Booking as BookingDB
from models.db_models import User, UserRole
from models.pydantic.booking import Booking, BookingCreate, BookingUpdate
from models.pydantic.pagination import PaginationParams, BookingFilterParams, SortParams, PaginatedResponse
from services import booking_service
from services.auth_service import get_current_user, require_role
from services.booking_service import get_booking_with_permission_check

router = APIRouter(
    prefix="/bookings",
    tags=["bookings"]
)

# Get all bookings endpoint - admin only with filtering and pagination
@router.get("/", response_model=PaginatedResponse[Booking])
async def get_bookings(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    status: str | None = Query(None, description="Filter by booking status"),
    car_id: int | None = Query(None, description="Filter by car ID"),
    start_date_from: str | None = Query(None, description="Filter bookings with start date from"),
    start_date_to: str | None = Query(None, description="Filter bookings with start date to"),
    end_date_from: str | None = Query(None, description="Filter bookings with end date from"),
    end_date_to: str | None = Query(None, description="Filter bookings with end date to"),
    sort_by: str = Query("id", description="Field to sort by"),
    sort_order: str = Query("asc", description="Sort order (asc or desc)"),
    db: Session = Depends(get_db), 
    _=Depends(require_role([UserRole.ADMIN]))
):
    """
    Get all bookings with filtering, sorting and pagination.
    Admin only endpoint.
    """
    pagination = PaginationParams(page=page, page_size=page_size)
    filters = BookingFilterParams(
        status=status,
        car_id=car_id,
        start_date_from=start_date_from,
        start_date_to=start_date_to,
        end_date_from=end_date_from,
        end_date_to=end_date_to
    )
    sort_params = SortParams(sort_by=sort_by, sort_order=sort_order)
    
    try:
        return booking_service.get_filtered_bookings(db, pagination, filters, sort_params=sort_params)
    except InvalidDateFormatException as e:
        raise HTTPException(
            status_code=api_status.HTTP_400_BAD_REQUEST, 
            detail=e.message
        )

# Get user's own bookings with filtering and pagination
@router.get("/my", response_model=PaginatedResponse[Booking])
async def get_my_bookings(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    status: str | None = Query(None, description="Filter by booking status"),
    car_id: int | None = Query(None, description="Filter by car ID"),
    start_date_from: str | None = Query(None, description="Filter bookings with start date from"),
    start_date_to: str | None = Query(None, description="Filter bookings with start date to"),
    end_date_from: str | None = Query(None, description="Filter bookings with end date from"),
    end_date_to: str | None = Query(None, description="Filter bookings with end date to"),
    sort_by: str = Query("id", description="Field to sort by"),
    sort_order: str = Query("asc", description="Sort order (asc or desc)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all bookings for the currently authenticated user with filtering, sorting and pagination
    """
    pagination = PaginationParams(page=page, page_size=page_size)
    filters = BookingFilterParams(
        status=status,
        car_id=car_id,
        start_date_from=start_date_from,
        start_date_to=start_date_to,
        end_date_from=end_date_from,
        end_date_to=end_date_to
    )
    sort_params = SortParams(sort_by=sort_by, sort_order=sort_order)
    
    try:
        return booking_service.get_filtered_bookings(
            db, pagination, filters, user_id=current_user.id, sort_params=sort_params
        )
    except InvalidDateFormatException as e:
        raise HTTPException(
            status_code=api_status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )

@router.get("/{booking_id}", response_model=Booking)
async def get_booking(
    booking: BookingDB = Depends(get_booking_with_permission_check)
):
    """Get booking by ID. Users can only access their own bookings unless they are admins."""
    return booking

@router.post("/", response_model=Booking, status_code=api_status.HTTP_201_CREATED)
async def create_booking(
    booking_data: BookingCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    
    try:
        return booking_service.create_booking(booking_data, current_user.id, db)
    except NoCarFoundException as e:
        raise HTTPException(
            status_code=api_status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except (
        CarNotAvailableException,
        BookingOverlapException,
    ) as e:
        raise HTTPException(
            status_code=api_status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except CurrencyServiceUnavailableException as e:
        raise HTTPException(
            status_code=api_status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=e.message
        )

@router.put("/{booking_id}", response_model=Booking)
async def update_booking(
    booking: BookingDB = Depends(get_booking_with_permission_check),
    booking_update: BookingUpdate = Body(...),
    db: Session = Depends(get_db)
):
    """Update a booking. Users can only update their own bookings unless they are admins."""
    try:
        # Pass the booking ID from the retrieved booking object
        return booking_service.update_booking(booking.id, booking_update, db)
    except (
        BookingStateException,
        DateRangeException, 
        BookingOverlapUpdateException,
        PickupAfterReturnException,
        FutureDateException,
        ReturnWithoutPickupException,
        DateOutsideBookingPeriodException,
        InvalidDateFormatException
    ) as e:
        raise HTTPException(
            status_code=api_status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except CurrencyServiceUnavailableException as e:
        raise HTTPException(
            status_code=api_status.HTTP_503_SERVICE_UNAVAILABLE, 
            detail=e.message
        )