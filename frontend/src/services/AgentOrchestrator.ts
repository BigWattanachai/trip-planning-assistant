import { ActivityAgent } from './agents/ActivityAgent';
import { RestaurantAgent } from './agents/RestaurantAgent';
import { BaseAgent } from './agents/BaseAgent';

interface TripInput {
  departure: string;
  destination: string;
  startDate: string;
  endDate: string;
  budgetRange: string;
}

export class AgentOrchestrator {
  private agents: Map<string, BaseAgent>;

  constructor() {
    this.agents = new Map();
    this.registerAgents();
  }

  private registerAgents() {
    this.agents.set('activity', new ActivityAgent());
    this.agents.set('restaurant', new RestaurantAgent());
    // Add more agents as needed
  }

  public async planTrip(userInput: TripInput) {
    try {
      // Run agents in parallel for faster processing
      const [activityResult, restaurantResult] = await Promise.all([
        this.agents.get('activity')?.execute({
          destination: userInput.destination,
          budget: userInput.budgetRange,
        }),
        this.agents.get('restaurant')?.execute({
          destination: userInput.destination,
          budget: userInput.budgetRange,
        }),
      ]);

      // Combine results from all agents
      return {
        success: true,
        data: {
          activities: activityResult?.data || [],
          restaurants: restaurantResult?.data || [],
          // Add more data from other agents
        },
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred',
      };
    }
  }
}
