import { BaseAgent, AgentResponse } from './BaseAgent';

interface Restaurant {
  id: string;
  name: string;
  cuisine: string;
  priceRange: string;
  rating: number;
  reviewHighlight: string;
  imageUrl: string;
}

interface RestaurantSearchParams {
  destination: string;
  budget?: string;
  cuisinePreferences?: string[];
}

export class RestaurantAgent extends BaseAgent {
  constructor() {
    super({
      name: 'RestaurantAgent',
      description: 'Agent for finding restaurants and dining experiences',
    });
  }

  public async execute<T = Restaurant[]>(params: RestaurantSearchParams): Promise<AgentResponse<T>> {
    // Mock data for restaurants
    const mockRestaurants: Restaurant[] = [
      {
        id: '1',
        name: 'ร้านทิพย์สมัย ผัดไทยประตูผี',
        cuisine: 'Thai',
        priceRange: '฿฿',
        rating: 4.7,
        reviewHighlight: 'ผัดไทยที่ดีที่สุดในกรุงเทพฯ รสชาติต้นตำรับ',
        imageUrl: 'https://images.unsplash.com/photo-1559314809-0d155014e29e?w=800&auto=format&fit=crop&q=60',
      },
      {
        id: '2',
        name: 'บ้านอาหารเรือนไทย',
        cuisine: 'Thai Fine Dining',
        priceRange: '฿฿฿',
        rating: 4.6,
        reviewHighlight: 'บรรยากาศสุดคลาสสิก อาหารไทยรสเลิศ',
        imageUrl: 'https://images.unsplash.com/photo-1543352634-a1c51d9f1fa7?w=800&auto=format&fit=crop&q=60',
      },
      {
        id: '3',
        name: 'Jay Fai',
        cuisine: 'Thai Street Food',
        priceRange: '฿฿฿',
        rating: 4.9,
        reviewHighlight: 'ร้านริมทางระดับมิชลินสตาร์ ปูผัดผงกะหรี่เด็ด',
        imageUrl: 'https://images.unsplash.com/photo-1601050690597-df0568f70950?w=800&auto=format&fit=crop&q=60',
      },
    ];

    return {
      success: true,
      data: mockRestaurants as unknown as T,
    };
  }
}
