import { BaseAgent, AgentResponse } from './BaseAgent';

interface Activity {
  id: string;
  name: string;
  description: string;
  rating: number;
  openingHours: string;
  imageUrl: string;
  category: string;
}

interface ActivitySearchParams {
  destination: string;
  preferences?: string[];
  budget?: string;
}

export class ActivityAgent extends BaseAgent {
  constructor() {
    super({
      name: 'ActivityAgent',
      description: 'Agent for finding activities and attractions at destinations',
    });
  }

  public async execute<T = Activity[]>(params: ActivitySearchParams): Promise<AgentResponse<T>> {
    // Mock data for activities
    const mockActivities: Activity[] = [
      {
        id: '1',
        name: 'วัดพระแก้ว',
        description: 'วัดที่มีชื่อเสียงที่สุดในกรุงเทพฯ เป็นที่ประดิษฐานพระแก้วมรกต',
        rating: 4.8,
        openingHours: '8:30 AM - 3:30 PM',
        imageUrl: 'https://images.unsplash.com/photo-1563492065599-3520f775eeed?w=800&auto=format&fit=crop&q=60',
        category: 'Cultural',
      },
      {
        id: '2',
        name: 'ตลาดนัดจตุจักร',
        description: 'ตลาดนัดที่ใหญ่ที่สุดในประเทศไทย มีสินค้ามากกว่า 15,000 ร้านค้า',
        rating: 4.5,
        openingHours: 'Sat-Sun: 9:00 AM - 6:00 PM',
        imageUrl: 'https://images.unsplash.com/photo-1577719996642-edf11c65fe76?w=800&auto=format&fit=crop&q=60',
        category: 'Shopping',
      },
      {
        id: '3',
        name: 'ล่องเรือแม่น้ำเจ้าพระยา',
        description: 'ชมทิวทัศน์สองฝั่งแม่น้ำเจ้าพระยายามค่ำคืน พร้อมอาหารไทยชั้นเลิศ',
        rating: 4.7,
        openingHours: '6:00 PM - 10:00 PM',
        imageUrl: 'https://images.unsplash.com/photo-1587974928442-77dc3e0dba72?w=800&auto=format&fit=crop&q=60',
        category: 'Experience',
      },
    ];

    return {
      success: true,
      data: mockActivities as unknown as T,
    };
  }
}
