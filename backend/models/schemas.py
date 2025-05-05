from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Any, Union
from datetime import datetime, date
from enum import Enum

class BudgetRange(str, Enum):
    BUDGET = "budget"
    MEDIUM = "medium"
    LUXURY = "luxury"

class TripRequest(BaseModel):
    departure: str
    destination: str
    startDate: str
    endDate: str
    budgetRange: BudgetRange = BudgetRange.MEDIUM
    preferences: Optional[Dict[str, Any]] = None
    
    @validator('startDate', 'endDate')
    def validate_date_format(cls, v):
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError("Date must be in format YYYY-MM-DD")
    
    @validator('endDate')
    def validate_end_date_after_start_date(cls, v, values):
        if 'startDate' in values:
            start = datetime.strptime(values['startDate'], "%Y-%m-%d")
            end = datetime.strptime(v, "%Y-%m-%d")
            if end <= start:
                raise ValueError("End date must be after start date")
        return v

class Activity(BaseModel):
    id: str
    name: str
    description: str
    rating: float
    openingHours: str
    imageUrl: str
    category: str
    duration: Optional[str] = None
    location: Optional[Dict] = None
    price: Optional[Dict] = None
    bookingUrl: Optional[str] = None
    recommendation: Optional[str] = None
    bestTimeToVisit: Optional[str] = None

class Restaurant(BaseModel):
    id: str
    name: str
    cuisine: str
    priceRange: str
    rating: float
    reviewHighlight: str
    imageUrl: str
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    hours: Optional[Dict] = None
    menuHighlights: Optional[List[str]] = None
    recommendation: Optional[str] = None
    bestTimeToVisit: Optional[str] = None
    reservationTips: Optional[str] = None

class FlightTime(BaseModel):
    airport: str
    code: str
    time: str
    terminal: Optional[str] = None

class Flight(BaseModel):
    id: str
    airline: str
    flightNumber: str
    departure: FlightTime
    arrival: FlightTime
    duration: str
    stops: int = 0
    price: float
    currency: str = "USD"
    class_: str = Field(alias="class")
    aircraft: Optional[str] = None
    baggage: Optional[Dict] = None
    amenities: Optional[List[str]] = None
    stopover: Optional[Dict] = None
    bookingUrl: Optional[str] = None
    direction: Optional[str] = None

class Accommodation(BaseModel):
    id: str
    name: str
    type: str
    rating: float
    reviewCount: int
    price: float
    priceUnit: str
    amenities: List[str]
    imageUrl: str
    platform: str
    bookingUrl: str
    address: Optional[str] = None
    location: Optional[Dict] = None
    roomTypes: Optional[List[Dict]] = None
    policies: Optional[Dict] = None
    highlights: Optional[List[str]] = None
    recommendation: Optional[str] = None
    locationScore: Optional[float] = None
    valueScore: Optional[float] = None

class Video(BaseModel):
    id: str
    title: str
    description: str
    thumbnail: str
    embedUrl: str
    duration: str
    viewCount: str
    likeCount: Optional[str] = None
    publishedAt: Optional[str] = None
    channelTitle: Optional[str] = None
    tags: Optional[List[str]] = None
    category: Optional[str] = None
    transcript_summary: Optional[str] = None

class TripResponse(BaseModel):
    destination: str
    departure: str
    startDate: str
    endDate: str
    budget: str
    activities: List[Activity]
    restaurants: List[Restaurant]
    flights: List[Flight]
    accommodations: List[Accommodation]
    videos: List[Video]
    summary: str
    requestId: str
    createdAt: str

class ChatMessage(BaseModel):
    message: str
    sessionId: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    sessionId: str
    timestamp: str

class WeatherCondition(BaseModel):
    date: str
    temperature: float
    description: str
    humidity: Optional[float] = None
    precipitation: Optional[float] = None
    icon: Optional[str] = None

class WeatherInfo(BaseModel):
    destination: str
    currentConditions: str
    temperature: Optional[float] = None
    forecast: List[WeatherCondition] = []
    lastUpdated: str

class CurrencyInfo(BaseModel):
    originCurrency: str
    destinationCurrency: str
    exchangeRate: Optional[float] = None
    lastUpdated: str

class DestinationInfo(BaseModel):
    destination: str
    overview: str
    highlights: List[str] = []
    weather: Optional[WeatherInfo] = None
    currency: Optional[CurrencyInfo] = None
    bestTimeToVisit: Optional[str] = None
    safetyInfo: Optional[str] = None
    localTips: List[str] = []
