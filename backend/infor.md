
Freedium
ko-fi
librepay
patreon
< Go to the original

Preview image
From Zero to Multi-Agents: A Beginner's Guide to Google Agent Development Kit (ADK)
A Hands-On Tutorial for Building Your First AI Agents with Google ADK
Dr Sokratis Kartakis
Dr Sokratis Kartakis

Follow
androidstudio
·
April 9, 2025 (Updated: April 9, 2025)
·
Free: No
Overview
If you're keeping up with AI, you've undoubtedly noticed the buzz around 'AI agents' — sophisticated programs built to act autonomously. Toolkits like CrewAI and LangChain have paved the way, offering structures for developing and managing these agents. But what function do these AI agent frameworks serve? Think of them as comprehensive software platforms created to streamline how AI agents are built, launched, and maintained. By providing essential building blocks for agent architecture, task management, and communication protocols, they empower developers to innovate faster, without getting bogged down in foundational plumbing.

Entering this dynamic field with its own comprehensive offering, Google has introduced the Google Agent Development Kit (ADK), an open-source Python library. Think of ADK as a toolkit designed to streamline the entire process of creating, testing, and launching sophisticated AI agents. Whether you need a chatbot that understands natural language or a behind-the-scenes process automation, ADK provides the structure and tools to build robust solutions.

While ADK is versatile, it truly shines when you need more than one agent to get the job done. Building complex applications often requires breaking down tasks into smaller, manageable parts, each handled by a specialized component. ADK is specifically designed for this:

Modular Agent Design: At its core, ADK lets you build individual Agents. These are the fundamental building blocks, like specialized team members. Some agents might use powerful Large Language Models (LLMs like Gemini, but not limited) for reasoning and conversation, while others act as controllers, directing the workflow.
Collaboration and Orchestration: ADK provides ways for these agents to work together. You can set up structured workflows (like steps in a sequence) or allow agents to dynamically decide how to collaborate based on the situation. Imagine a lead agent delegating tasks to others!
Giving Agents Abilities (Easy Tool Creation): An agent isn't limited to just talking. ADK makes it particularly easy to create and equip agents with custom Tools — often based on simple Python functions you write yourself. These tools act as special abilities allowing agents to interact with the outside world, whether it's searching the web, running calculations, accessing databases, or even calling other specialized agents.
Beyond these core building blocks, a key differentiator for ADK is its comprehensive suite for interacting with, managing, and deploying your agents. Whether you prefer working via a command-line terminal (CLI), using an interactive console for debugging, deploying agents within containers, managing them through the provided Angular-based UI, or bringing them to life with real-time conversation by wrapping the Gemini Live Streaming API, ADK offers flexible interfaces to support the entire development and deployment lifecycle.

In this blog post, we aim to give you a practical introduction to Google ADK's main capabilities using this powerful library. We'll guide you step-by-step through building increasingly complex solutions:

Starting with the basics: Creating a simple agent without any tools.
Adding capabilities: Enhancing a single agent by giving it tools.
Building our goal: Constructing the multi-agent teaching assistant example.
Taking the next step: Briefly showing how you can deploy an agent built with ADK on Google Cloud Vertex AI Agent Engine.
For this walkthrough, we will be using code examples available in this GitHub Repository (adk-walthrough) so you can easily follow along and experiment yourself. Let's get started!

Google ADK Walkthrough: Your Step-by-Step Development Tutorial
Get ready to dive deep and get hands-on with the Google Agent Development Kit! This walkthrough section provides a practical, step-by-step guide to building your first agent-base solutions using the ADK library and code from our companion repository.

We'll start with the Prerequisites, ensuring your development environment is correctly set up — from installing ADK in a Python virtual environment to configuring necessary access credentials. Running a simple test script will confirm everything is ready to go.

Then, we'll progress through four core chapters:

The Basic Agent: You'll learn how to instantiate your very first agent, defining its core instructions and interacting with it. We'll explore fundamental ADK components like the Agent class, the Runner, and basic session management (InMemorySessionService).
Single Agent with Tools: We'll enhance our agent by giving it abilities! You'll see how to create custom tools using simple Python functions (complete with essential docstrings) and how the agent leverages these tools to perform tasks, like mathematical calculations. We'll also cover how to handle the event stream for tool calls and responses.
Multi-Agent Interaction: This is where we bring it all together. You'll learn how to design a system where multiple specialized agents collaborate. We'll build an orchestrator agent (a "teacher's assistant") that delegates tasks to child agents (like our math agent and a new grammar agent), demonstrating the power of the sub_agents parameter and defining interaction flows.
(Bonus) Agent Deployment to the Cloud: We'll briefly touch upon the concepts and potential next steps involved in taking your agent application from local development to a live deployment, particularly focusing on cloud environments leveraging Google Cloud Agent Engine.
Throughout this walkthrough, we'll reference specific Python files (chapter1_main_basic.py, chapter2_main_single_agent.py, chapter3_main_multi_agent.py, chapter4_agent_deployment.py) from the repository, allowing you to follow along directly, building a functioning multi-agent application and understanding the path towards deployment. Let's get started!

Prerequisites
Understand Agent Development Kit and its capabilities by reading the adk-docs Open Source page and google-adk PyPI project page.

Clone the walkthrough repository: GitHub Repository (adk-walthrough)

Copy
git clone https://github.com/sokart/adk-walkthrough.git
Create a new Python virtual environment (note: Python 3.11 is preferred, otherwise you should use the — ignore-requires-python parameter in pip3 install):

Copy
python -m venv .adk_venv
source .adk_venv/bin/activate
Install Agent Development Kit:

Copy
pip install google-adk==0.1.0
Copy "dotenv.example" file and rename it to .env. Fill the Project, Location, and Default Model details as global parameters:

Copy
GOOGLE_GENAI_USE_VERTEXAI=1
GOOGLE_CLOUD_PROJECT=FILL_YOUR_PROJECT_ID
GOOGLE_CLOUD_LOCATION=FILL_YOUR_LOCATION
MODEL=FILL_THE_DEFAULT_MODEL
Example:

Copy
GOOGLE_GENAI_USE_VERTEXAI=1
GOOGLE_CLOUD_PROJECT=gcp-project-genai
GOOGLE_CLOUD_LOCATION=us-central1
MODEL='gemini-2.0-flash-001'
Run your first agent example in a terminal, chapter1_main_basic.py. This is the simplest example of how to call an agent without tools. This will prove that you have setup the above correctly:

Copy
> python3 chapter1_main_basic.py

User Query: Hi, how are you?
- - - - - - - - - - - - - - -
>>> Inside final response <<<
- - - - - - - - - - - - - - -
Agent: basic_agent
Response time: 1675.186 ms
Final Response:
I am doing well, thank you for asking. How can I help you today?
- - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Uncomment the last seven lines in chapter1_main_basic.py to test multiple queries with the agent.

If everything works, you have achieved to set up the Agent Development Kit correctly. Let's deep dive on the key components of the basic agent.

For Chapter 4, you need some additional prerequisites. First, enable CloudTrace API by visiting the service page at Google Cloud Project console. Then, install Vertex AI AgentEngine dependencies:

Copy
pip install google-cloud-aiplatform[adk,agent_engines]
Chapter 1. The Basic Agent
None
Image by author
This chapter provides a hands-on introduction to creating and interacting with a basic agent using the Agent Development Kit. We'll walk through the process of defining an agent's core attributes, including its name, the underlying language model, and crucial instructions that govern its behavior. The chapter focuses on building a simple agent without any external tools, emphasizing the fundamental functionality of the framework. We'll demonstrate how to send both single and multiple queries to the agent, illustrating how to initiate conversations and receive responses. The primary goal of this chapter is to familiarize readers with the Agent Development Kit's basic building blocks and core interaction patterns, laying the groundwork for more complex agent development in later chapters.

To achieve the above we will use from the repository chapter1_main_basic.py

Instantiate an Agent
The first step in building an agent is to import the necessary packages from the Agent Development Kit and other required libraries.

Copy
# Import libraries from the Agent Development Kit
from google.adk.agents import Agent
from google.adk.artifacts import InMemoryArtifactService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
Having imported the necessary packages let's instantiate our first agent.

Copy
# Create a basic agent with name, description, and instructions only
basic_agent = Agent(model=MODEL,
name="agent_basic",
description="This agent responds to inquiries about its creation by stating it was built using the Google Agent Development Kit.",
instruction="If they ask you how you were created, tell them you were created with the Google Agent Development Kit.",
generate_content_config=types.GenerateContentConfig(temperature=0.2),)
With the above snippet, we instantiate an Agent object, configuring its fundamental properties. This includes specifying the underlying language model (MODEL e.g ."gemini-2.0-flash-001" ), giving the agent a descriptive name (agent_basic), and providing a description of its role. A clear description helps other users (or agents as we will describe in the later chapters) understand the agent's role and how it can be utilized.

Most importantly, we define the agent's instruction (i.e instruction prompt), which provides its core programming by dictating its behavior in response to specific queries.

Lastly, we configure the model's content generation settings (which are similar to Gemini configuration requests), and we provide as example the temperature, which influences the randomness of the agent's responses.

This instantiation effectively brings the agent to life, defining its essential characteristics and how it should interact with users.

Interact with an Agent
Up to this point we have created the agent but how could we start interaction with it? To start using the Agent we need first to instantiate the memory of the Agent. We are going to use two different types of memory for our agent (currently supported by ADK):

Memory Session: Stores the conversational history (messages exchanged), the agent's internal state (variables, etc.), and other data related to a specific interaction. It's ephemeral in this in-memory implementation.
Memory Artifact: Stores files or data generated or used by the agent. These could be text files, images, or any other kind of data. Like sessions, these are lost when the program ends in the in-memory version.
Copy
session_service = InMemorySessionService()
artifact_service = InMemoryArtifactService()
In this first chapter we are not using the memory artifact service. Both the session_service and artifact_service are configured to store data directly in the runtime's memory (for example, your laptop's RAM if you're running the code locally).

With the memory configuration set up, the next step is to begin using the agents. To do this, we need to create a new session and prepare the content (i.e. query) for the agent, similar to how you might interact with a model like Gemini. The session is a fundamental component of an Agent, as it holds crucial details like event history, status, memory contents, event and flags, and other operational information.

Copy
AGENT_APP_NAME = 'agent_basic'

def send_query_to_agent(agent, query):
session = session_service.create_session(app_name=AGENT_APP_NAME,
user_id='user',)

content = types.Content(role='user', parts=[types.Part(text=query)])
In this example, we initialize a new session for each query sent to the agent. This approach ensures that every interaction is treated independently, without maintaining any memory or context from previous queries — each query is processed in isolation.

However, if you require multi-turn conversations where the agent remembers previous exchanges, you'll need to adjust this. Instead of creating a session per query, create the session object once, before making any calls to the send_query_to_agent function. Then, reuse that same session object for each subsequent query in the conversation.

Everything is ready to run our first interaction with the agent. To achieve this we need first to create a Runner and then run it:

Copy
runner = Runner(app_name=AGENT_APP_NAME,
agent=agent,
artifact_service=artifact_service,
session_service=session_service)

events = runner.run(user_id='user'
session_id=session.id,
new_message=content,)
A Runner is the component responsible for executing an agent's logic. It's the engine that drives the interaction between the user's query, the agent's instructions, the language model, and any tools the agent might use. Here's a breakdown of what the Runner does:

Orchestrates Agent Execution: The Runner takes a user's query, the agent's definition (including its instructions, model, and tools), and a session context. It then manages the process of sending the query to the LLM, interpreting the LLM's response, calling any necessary tools, and updating the agent's state.
Manages Sessions and Artifacts: The Runner works in conjunction with the SessionService and ArtifactService to maintain the context of the conversation (the session) and manage any files or data (artifacts) the agent uses or creates.
Handles Event Stream: When an agent runs, it generates a stream of events. These events can include things like: — The LLM's response. — A tool being called. — The result of a tool call. — The agent's final response. The Runner is responsible for processing this stream of events and making them available to the application.
In this chapter, our agent doesn't have any tools. Therefore, the agent will return just a final response. To parse the event(s) and retrieve the final response, we used the following:

Copy
for _, event in enumerate(events):
is_final_response = event.is_final_response()
if is_final_response:
final_response = event.content.parts[0].text
The last step is to call the send_query_to_agent function with a new prompt:

Copy
send_query_to_agent(basic_agent, "Hi, how are you?")
This will execute the code, interact with the agent and return the final response as presented in the previous section.

Copy
> python chapter1_main_basic.py

User Query: Hi, how are you?
- - - - - - - - - - - - - - -
>>> Inside final response <<<
- - - - - - - - - - - - - - -
Agent: agent_basic
Response time: 1868.995 ms
Final Response:
I am doing well, thank you for asking. How can I help you today?
- - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Lastly, we can interact with multiple consequent queries using the following example:

Copy
queries = ["Hi, I am Tom",
"Could you let me know what you could do for me?",
"How were you built?",]

for query in queries:
send_query_to_agent(basic_agent, query)
Try to change the input queries and test your agent further.

Congratulations, you have successfully completed Chapter 1. In the next chapter we will focus on creating our first tools.

Chapter 2. Single Agent with Tools
None
Image by author
Now that you have understood the main components of the agents, it is time to introduce tools. Tools are nothing else than a list of Python functions that your agent is able to use.

Create an Agent with Tools
For this chapter we will use the chapter2_main_single_agent.py and the math agent into agent_maths/agent.py. In the agent_maths folder, and agent.py file, we have created an agent that uses multiple functions to solve mathematical calculations. First, we had to define the functions. Here is an example of a function that adds all the numbers in a list:

Copy
def add(numbers: list[int]) -> int:
"""Calculates the sum of a list of integers.

    This function takes a list of integers as input and returns the sum of all
    the elements in the list. It uses the built-in `sum()` function for
    efficiency.
    
    Args:
        numbers: A list of integers to be added.

    Returns:
        The sum of the integers in the input list. Returns 0 if the input
        list is empty.
    
    Examples:
        add([1, 2, 3]) == 6
        add([-1, 0, 1]) == 0
        add([]) == 0
    """
    return sum(numbers)
Even if we have a very simple function, we have added a descriptive Docstring (i.e. text in """ … """). The reason for this is that with the Docstring we pass to the agent the description of the function, the input parameters and return values. These details are really important to enable the agent to select the right tool and identify the parameter correctly. If docstring is missing the agent might never call the tool. For the readers, familiar with Function Calling of Gemini, the docstring represents the Function Declaration.

Similarly, we define the subtract, multiply, and divide functions. But how do we pass those tools to the agent?

Copy
agent_math = Agent(model=MODEL,
name="simple_math_agent",
description="This agent performs basic arithmetic operations (addition, subtraction, multiplication, and division) on user-provided numbers, including ranges.",
instruction="""
I can perform addition, subtraction, multiplication, and division operations on numbers you provide.
Tell me the numbers you want to operate on.
For example, you can say 'add 3 5', 'multiply 2, 4 and 3', 'Subtract 10 from 20', 'Divide 10 by 2'.
You can also provide a range: 'Multiply the numbers between 1 and 10'.
""",
generate_content_config=types.GenerateContentConfig(temperature=0.2),
tools=[add, subtract, multiply, divide],)
We pass the function names to the tools list parameter.

You have just created your first agent to resolve mathematical calculations. The next step is to use it.

Interact with the Math Agent
By extending the code of chapter1_main_basic.py, we have created chapter2_main_single_agent.py that shows you an example how to interact with an agent with tools. Our code required only one modification into the send_query_to_agent, on how we decode the events. Specifically, in addition to the final response, we had to incorporate function calls and responses. Let's deep dive into it:

Copy
for _, event in enumerate(events):
print(f'Agent: {event.author}')
is_final_response = event.is_final_response()
function_calls = event.get_function_calls()
function_responses = event.get_function_responses()

    if is_final_response:
        final_response = event.content.parts[0].text
        print(f'Final Response {final_response}')
    elif function_calls:
        for function_call in function_calls:
            print(f'Call Function: {function_call.name}')
            print(f'Argument: {function_call.args}')
    elif function_responses:
        for function_response in function_responses:
            print(f'Function Name: {function_response.name}')
            print(f'Function Results: {function_response.response}')
This code snippet extracts key information from a single event within the agent's event stream. It checks if the event represents the final response, identifies any function calls made by the agent, and retrieves any function call responses.

Here's a breakdown:

Event Analysis:

is_final_response = event.is_final_response(): Checks if this event is the agent's final answer (True/False).
function_calls = event.get_function_calls(): Retrieves requested function calls within this event (returns a list of FunctionCall objects, empty if none).
function_responses = event.get_function_responses(): Retrieves results from executed functions included in this event (returns a list of FunctionResponse objects, empty if none).
Conditional Handling:

if is_final_response: Executes only for the final response event, processing the agent's ultimate answer.
elif function_calls: Executes if the event contains function call requests (but isn't final). It processes details about which functions/tools the agent wants to call and their arguments.
elif function_responses: Executes if the event contains function results (but isn't final or a call request). It processes the output received from executed functions/tools.
Now that you are familiar with the code modifications, run the chapter2_main_single_agent.py which will execute the following:

Copy
if __name__ == '__main__':
# Send a single query to the agent
send_query_to_agent(agent_math,"First multiply numbers 1 to 3 and then add 4")
The output should look like this:

Copy
>python chapter2_main_single_agent.py


User Query: First multiply numbers 1 to 3 and then add 4
- - - - - - - - - - - - - - -
+++ Inside function call +++
- - - - - - - - - - - - - - -
Agent: agent_math
Call Function: multiply
Argument: {'numbers': [1, 2, 3]}
- - - - - - - - - - - - - - - 
- Inside function response -
- - - - - - - - - - - - - - - 
Agent: agent_math
Function Name: multiply
Function Results: {'result': 6}
- - - - - - - - - - - - - - -
+++ Inside function call +++
- - - - - - - - - - - - - - -
Agent: agent_math
Call Function: add
Argument: {'numbers': [6, 4]}
- - - - - - - - - - - - - - - 
- Inside function response -
- - - - - - - - - - - - - - - 
Agent: agent_math
Function Name: add
Function Results: {'result': 10}
- - - - - - - - - - - - - - -
>>> Inside final response <<<
- - - - - - - - - - - - - - -
Agent: agent_math
Response time: 4685.989 ms
Final Response:
The answer is 10.
- - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Congratulations, you have just used your first Agent with custom tools! In the next chapter we will describe how you can connect multiple agents together.

Chapter 3. Multi-agent Interaction
None
Image by author
Having explored basic agents and agents equipped with tools in the previous chapters, we now turn our attention to a more sophisticated concept: multi-agent systems. This chapter introduces the creation of an agent that orchestrates the behavior of other specialized agents.

Building upon the math agent example from Chapter 2, which performs mathematical calculations, we introduce a new agent capable of grammar checking, and a summary agent to synthesize the final answer to the end user. These three agents, each with a specific function, will then be integrated into a fourth, higher-level agent: a "teacher's assistant." This assistant agent will receive input from a user (presumably a child), first validate the grammar of the input, correct it if necessary, and provide explanations. Then, it will delegate the mathematical calculation to the math agent. Finally, the summary agent will collect the outputs of both grammar and math agent and will produce the final output.

This multi-agent approach allows us to create more complex and robust systems by combining the strengths of specialized agents.

Create and Connect Multiple Agents
For this chapter we will use the chapter3_main_multi_agent.py, the new grammar agent we have implemented into agent_grammar/agent.py, the summary agent into agent_summary/agent.py and the math agent into agent_maths/agent.py.

None
Image by author
Before we start implementing the multi-agent interaction we need to have the specialized agents developed. Therefore, we need to describe briefly what the grammar and summary agents do. agent_grammar is designed to check and correct grammar in text. Similar to agent_math, it leverages a tool but in this case the tool calls Gemini to perform the grammar analysis and generate corrections and explanations. We selected this to show you that a tool can call another Foundation Model to perform more complex tasks. On the other hand, agent_summary, is an agent without tools responsible to synthesize the answer out of the other two agents. If we think for a moment, an agent without tools is like calling the model directly. As the scope of this walkthrough is to focus on the functionality of Agent Development Kit, we skip the details of the implementation of these agents. For further details, please see the source code of the corresponding agents.

Now that we have our specialized agents (agent_grammar, agent_math and agent_summary) ready, we create the "teacher's assistant" agent, agent_teaching_assistant, which will orchestrate their actions.

Copy
from google.adk.agents import SequentialAgent

agent_teaching_assistant = SequentialAgent(
name="agent_teaching_assistant",
description="This agent acts as a friendly teaching assistant, checking the grammar of kids' questions, performing math calculations using corrected or original text (if grammatically correct), and providing results or grammar feedback in a friendly tone.",
sub_agents=[agent_grammar, agent_math, agent_summary],)
The agent_teaching_assistant is created as an instance of ADK's SequentialAgent class. This type of agent orchestrates a workflow by executing a series of defined sub-agents sequentially — one completes before the next begins. Key parameters for initializing a SequentialAgent include its name, description, and the sub_agents list.

The sub_agents parameter is crucial; it's a list specifying the agents the parent (agent_teaching_assistant) will invoke in order. For instance, with sub_agents=[agent_grammar, agent_math, agent_summary], agent_teaching_assistant establishes a processing pipeline: first agent_grammar runs (handling grammar), then agent_math (handling calculations), and finally agent_summary (handling summarization). This defines a parent-child relationship where the SequentialAgent directs the sub-agents.

This specific sequential order is intentional for our example. We need grammar verified before attempting math, and the summary must reflect the outcome of both prior stages. ADK offers alternative flows like ParallelAgent for running sub-agents simultaneously, but that wouldn't suit the necessary step-by-step logic required here. If you need automatic sub-agent selection, you can configure this using the Agent Class with appropriate instructions in the prompt.

Note: Alternatively, agents can be defined as tools, but note the difference: an agent-as-tool receives only necessary input, whereas a sub-agent can access the complete session context. Here is an example of agents as tools:

Copy
from google.adk.tools.agent_tool import AgentTool

tool=[AgentTool(agent=agent_math)]
Interact with the Teaching Assistant Agent
A key advantage of ADK is its straightforward event handling, even for multi-agent scenarios. Specifically, the event parsing code presented in Chapter 2 can be reused without modification. We can directly use the send_query_to_agent function with our composite agent_teaching_assistant:

Copy
send_query_to_agent(agent_teaching_assistant,
"Hi teacher. Could she help me to multiply all the numbers between 1 and 10?")
Notice the intentional grammar error ("she" should be "you"). Let's see how our SequentialAgent handles this query:

Copy
> python chapter3_main_multi_agent.py


User Query: Hi teacher. Could she help me to multiply all the numbers between 1 and 10?
- - - - - - - - - - - - - - -
>>> Inside final response <<<
- - - - - - - - - - - - - - -
Agent: agent_grammar
Response time: 2379.755 ms
Final Response:
Hi! The corrected text is:
Could you help me to multiply all the numbers between 1 and 10?
There were a couple of little things! First, "she" should be "you" because you're asking me, not someone else. Also, I added "you" to make it a question addressed to me. "Could you" is a polite way to ask for help!
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

- - - - - - - - - - - - - - -
+++ Inside function call +++
- - - - - - - - - - - - - - -
Agent: agent_math
Call Function: multiply
Argument: {'numbers': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}
- - - - - - - - - - - - - - - 
- Inside function response -
- - - - - - - - - - - - - - - 
Agent: agent_math
Function Name: multiply
Function Results: {'result': 3628800}
- - - - - - - - - - - - - - -
>>> Inside final response <<<
- - - - - - - - - - - - - - -
Agent: agent_math
Response time: 5738.92 ms
Final Response:
The result of multiplying all the numbers between 1 and 10 is 3628800.
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

- - - - - - - - - - - - - - -
>>> Inside final response <<<
- - - - - - - - - - - - - - -
Agent: agent_summary
Response time: 7968.78 ms
Final Response:
Hi there! That's a super interesting question! 😊
First, let's look at how we asked it. Sometimes changing a word or two can make our questions even clearer! Instead of "Could she help me," saying it like this: "Could you help me to multiply all the numbers between 1 and 10?" is perfect. The little change we made was using "you" because you're talking to me! Well done for asking for help so nicely! 👍
Now, for the math part you asked about! The answer is: 3628800. That's a really big number!
Great job asking your question and doing the math thinking! Keep up the fantastic work and keep asking questions! ✨
- - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Congratulations, you have just implemented your first multi-agent solution! In the next chapter, we will describe how you can deploy this agent using the Google Cloud Agent Engine and interact with it.

(Bonus) Chapter 4. Agent Deployment to the Cloud
None
Image by author
In the previous chapter, we successfully built agent_teaching_assistant, a multi-agent system using the ADK's SequentialAgent. It cleverly combined grammar checking, mathematical calculation, and summarization. That's great for running locally, but the real power comes when you deploy it as a scalable, accessible service.

This bonus chapter provides a walkthrough on deploying our agent_teaching_assistant to Google Cloud Vertex AI Agent Engine. Vertex AI Agent Engine is a fully managed Google Cloud service designed to streamline the deployment, management, and scaling of AI agents in production. By handling the infrastructure complexities, it allows developers to focus on creating intelligent applications using various Python frameworks like ADK, LangGraph, and Langchain, leveraging available foundation models and tools. The service offers simplified development by abstracting low-level tasks, integrated quality evaluation, robust security features, and comprehensive management capabilities, making it easier to bring AI agents to production reliably and efficiently. By deploying, we make our agent available via an API endpoint, ready to be integrated into applications or called directly.

ADK provides flexibility by supporting two primary modes for running your agent with Agent Engine:

Local Simulation: Ideal for rapid development, testing, and debugging directly on your machine using AdkApp.
Remote Deployment: Packages and deploys your agent to the managed Agent Engine service on Google Cloud using agent_engines.create. (Note: Currently, April 2025, remote deployment requires Python 3.8 to 3.12 due to current cloud environment support).
Our script uses an IS_REMOTE_DEPLOYMENT flag to easily switch between these modes (set to 0 for local, 1 for remote). Let's look at the code that handles this:

Copy
from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp

if(IS_REMOTE_DEPLOYMENT == 0):
deployed_agent = AdkApp(agent=agent_teaching_assistant,enable_tracing=True,)
else:
deployed_agent = agent_engines.create(agent_teaching_assistant,
requirements=["google-cloud-aiplatform[adk,agent_engines]"])
Local Simulation (IS_REMOTE_DEPLOYMENT == 0): We instantiate AdkApp from vertexai.preview.reasoning_engines. This class serves as a local simulator for the Agent Engine runtime. It's perfect for quickly testing agent logic changes without waiting for cloud deployment. The key parameters used here are:

agent=agent_teaching_assistant: This injects our defined SequentialAgent into the local runner.
enable_tracing=True: This activates detailed execution tracing, sending data to Google Cloud Trace, which is extremely helpful for visualizing the agent's internal steps and debugging complex interactions.
Remote Deployment (IS_REMOTE_DEPLOYMENT == 1): We call the vertexai.agent_engines.create function. This command packages your agent code and dependencies and initiates the deployment to the managed Agent Engine service on Google Cloud. Besides passing the object object (e.g. agent_teaching_assistant), you must specify:

requirements: A list detailing the Python package dependencies needed to run your agent in the cloud. This includes libraries installable from PyPI (like google-cloud-aiplatform) and paths to local libraries (e.g. wheel files) if necessary. Version pinning might be necessary for stability.
extra_packages (optional): A list specifying local files or directories that need to be bundled and uploaded with your deployment.
This deployment process takes several minutes while Agent Engine builds the underlying container image and provisions the service endpoint.

After the agent is either initialized locally (AdkApp) or the remote deployment process is initiated (agent_engines.create), the script proceeds to interact with it. A significant advantage of the ADK and Agent Engine integration is that the interaction code remains identical for both modes.

The deployed_agent object you get back (whether it's the local AdkApp instance or the handle returned by agent_engines.create referencing the remote service) exposes the same methods. This means your code for managing sessions (create_session, list_sessions, get_session) and sending queries (stream_query) works seamlessly whether you're testing locally or interacting with the deployed cloud instance.

Interactions typically happen within a session context. The script demonstrates basic session management:

Copy
#Create a new session for a specific user
session = deployed_agent.create_session(user_id="user")
print(" - - - - - - - - - - - - - - -")
print('>>> New session details <<<')
print(" - - - - - - - - - - - - - - -")
print(session) # Display the created session object

# Optionally list all sessions for that user
print(" - - - - - - - - - - - - - - -")
print('>>>>>> List sessions <<<<<<')
print(" - - - - - - - - - - - - - - -")
print(deployed_agent.list_sessions(user_id="user"))

# Optionally get details for the specific session again
print(" - - - - - - - - - - - - - - -")
print('>>>>>> Get sessions <<<<<<')
print(" - - - - - - - - - - - - - - -")
session = deployed_agent.get_session(user_id="user", session_id=session.id)
print(session)
create_session(user_id=…): Establishes a new conversation context, returning a session object with a unique ID.
list_sessions(user_id=…): Retrieves all active sessions for the given user.
get_session(user_id=…, session_id=…): Fetches details for one specific session.
The output clearly shows the details of the newly created session:

Copy
- - - - - - - - - - - - - - -
>>> New session details <<<
 - - - - - - - - - - - - - - -
id='1213d6ad-ea8d-400f-8bf8–4d6b5995ad59' app_name='default-app-name' user_id='user' state={} events=[] last_update_time=1744068012.6078598
 - - - - - - - - - - - - - - -
>>>>>> List sessions <<<<<<
 - - - - - - - - - - - - - - -
sessions=[Session(id='1213d6ad-ea8d-400f-8bf8–4d6b5995ad59', app_name='default-app-name', user_id='user', state={}, events=[], last_update_time=1744068012.6078598)]
 - - - - - - - - - - - - - - -
>>>>>> Get sessions <<<<<<
 - - - - - - - - - - - - - - -
id='1213d6ad-ea8d-400f-8bf8–4d6b5995ad59' app_name='default-app-name' user_id='user' state={} events=[] last_update_time=1744068012.6078598
Now we send the actual query to the agent within the created session:

Copy
def parse_event_content(event: dict) -> list:
"""
Parses the 'content' section of an event dictionary to extract text,
function calls, or function responses from the 'parts' list.

    Args:
        event: The event dictionary to parse.
    
    Returns:
        A list of tuples. Each tuple contains (events type, content)
        Returns an empty list if the structure is invalid or no
        relevant parts are found.
    """
    results = []

    content = event.get('content')
    if not isinstance(content, dict):
        return results # Return empty list if content is missing/wrong type

    parts = content.get('parts')
    if not isinstance(parts, list):
        return results # Return empty list if parts is missing/wrong type

    # Iterate through each dictionary in the 'parts' list
    for part in parts:
        if not isinstance(part, dict):
            results.append(('unknown', part)) # Handle non-dict items
            continue # Skip to the next item
        
        if 'text' in part:
            print(" - - - - - - - - - - - - - - -")
            print('>>> Inside final response <<<')
            print(" - - - - - - - - - - - - - - -")
            print(part['text'])
            results.append(('text', part['text']))
        elif 'function_call' in part:
            print(" - - - - - - - - - - - - - - -")
            print('+++ Inside function call +++')
            print(" - - - - - - - - - - - - - - -")
            print(f"Call Function: {part['function_call']['name']}")
            print(f"Argument: {part['function_call']['args']}")
            # Found a function call part
            results.append(('function_call', part['function_call']))
        elif 'function_response' in part:
            print(" - - - - - - - - - - - - - - - ")
            print(' - Inside function response - ')
            print(" - - - - - - - - - - - - - - - ")
            print(f"Function Response: {part['function_response']['name']}")
            print(f"Response: {part['function_response']['response']}")
            results.append(('function_response', part['function_response']))
        else:
            # The part dictionary doesn't contain any of the expected keys
            print(f'Unknown part: {part}')
            results.append(('unknown', part))
    return results

# Send query to the deployed agent
events = deployed_agent.stream_query(user_id="user",
session_id=session.id,
message="Hi teacher. Could she help me to multiply all the numbers between 1 and 10?",)

# Parse events including final response, function call/response
for event in events:
parse_event_content(event)
stream_query function sends the message to the specified user_id and session_id. It returns an iterator (events) that yields event objects as the agent processes the request as we have seen in ADK. The for event in events: loop iterates through the stream. For each event, it calls our parse_event_content helper function. This helper identifies the type of event (final response text, function call request, function response data) and prints formatted output. Note that parsing those events has a slightly different format to unify multiple agent frameworks (e.g. LangChain), and, therefore, we had to create a different parser. However, the final output looks like the one from Chapter 3:

Copy
- - - - - - - - - - - - - - -
>>>> Interact with Agent <<<<
- - - - - - - - - - - - - - -
- - - - - - - - - - - - - - -
>>> Inside final response <<<
- - - - - - - - - - - - - - -
Hi! The corrected text is:
Hi teacher. Could you help me to multiply all the numbers between 1 and 10?
You used "she" instead of "you". "She" is used to talk about a girl or woman, but you wanted to ask your teacher directly for help, so we use "you". "You" is used when you're talking to someone.

- - - - - - - - - - - - - - -
+++ Inside function call +++
- - - - - - - - - - - - - - -
Call Function: multiply
Argument: {'numbers': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}
- - - - - - - - - - - - - - - 
- Inside function response -
- - - - - - - - - - - - - - - 
Function Response: multiply
Response: {'result': 3628800}
- - - - - - - - - - - - - - -
>>> Inside final response <<<
- - - - - - - - - - - - - - -
The result of multiplying all the numbers between 1 and 10 is 3628800.
- - - - - - - - - - - - - - -
>>> Inside final response <<<
- - - - - - - - - - - - - - -
Hi there! That's a super interesting question! 😊

First, let's look at how we asked it. Instead of saying "Could she help me?", saying "Could you help me?" is perfect. The little change we made was using "you" because you're talking directly to me, your teacher! Well done for asking for help! 👍

Now, for the math part you asked about! The answer is: 3628800. That's a really big number!

We figured that out by multiplying all the numbers from 1 all the way up to 10. It's like saying 1 x 2 x 3 x 4 x 5 x 6 x 7 x 8 x 9 x 10!

Great job asking your question and doing the math thinking! Keep up the fantastic work and keep asking questions! ✨
Congratulations! You've now seen how to take an ADK agent from local code to a deployed service on Google Cloud Agent Engine. This process involves setting up prerequisites like a staging bucket, defining dependencies, and using vertexai.agent_engines.create for remote deployment or AdkApp for local simulation. By deploying your agent, you unlock scalability and the ability to integrate, observe, evaluate your sophisticated multi-agent logic into real-world applications. From here, you can explore monitoring your deployed agent, updating it, or building client applications that consume its API.

Conclusion
We've journeyed through the essentials of the Google Agent Development Kit (ADK) in this post. Starting with the broader landscape of AI agent frameworks, we introduced ADK as Google's powerful, open-source Python library designed to simplify the creation, testing, and deployment of sophisticated agents. We specifically highlighted its strengths for building multi-agent solutions, the ease of creating custom Tools from Python functions, and its comprehensive interaction suite covering command-line, UI, containers, and live streaming capabilities.

Through our step-by-step walkthrough — building the teaching assistant example — you've seen ADK in action. We progressed practically from creating a simple agent without tools, to enhancing a single agent with custom abilities, and finally, to constructing a collaborative multi-agent system. We also took a quick look at the deployment process, completing the basic lifecycle.

Our goal was to provide you with a solid foundation and the confidence to start building your own innovative agent-based applications using Google ADK. The possibilities are vast, from automating simple tasks to orchestrating complex AI teams. We strongly encourage you to dive into the code examples provided in this GitHub Repository (adk-walthrough), experiment further, and explore the official Google adk-docs Open Source page and google-adk PyPI project page to unlock its full potential. For further examples, check out the Google prebuilt agents in this repository.

Happy building!

#agents
#google
#google-cloud-platform
#generative-ai-tools
#ai
