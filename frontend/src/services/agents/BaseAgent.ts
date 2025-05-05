interface AgentConfig {
  name: string;
  description: string;
  apiEndpoint?: string;
  apiKey?: string;
}

export interface AgentResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

export abstract class BaseAgent {
  protected config: AgentConfig;

  constructor(config: AgentConfig) {
    this.config = config;
  }

  protected async makeRequest<T>(endpoint: string, params?: any): Promise<AgentResponse<T>> {
    try {
      // Simulate API request
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // This is where you would make actual API calls
      // For now, we'll return mock data
      return {
        success: true,
        data: {} as T,
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  public abstract execute<T>(params: any): Promise<AgentResponse<T>>;
}
