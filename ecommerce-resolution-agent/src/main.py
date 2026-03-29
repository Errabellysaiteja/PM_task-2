import json
from crewai import Crew, Process
from crewai.tools import BaseTool  # <-- We import directly from CrewAI now!
from agents import ResolutionAgents
from tasks import ResolutionTasks
from rag_pipeline import get_retriever

# 1. Create the Custom Search Tool for the Retriever Agent
retriever = get_retriever()

# 2. Create a Custom Native CrewAI Tool Class
# By inheriting from BaseTool, CrewAI's strict validation will pass it perfectly.
class PolicySearchTool(BaseTool):
    name: str = "Policy Search Tool"
    description: str = "Searches the company policy database for relevant rules and returns text with citations."

    # The _run method is what the agent actually calls when it uses the tool
    def _run(self, query: str) -> str:
        docs = retriever.invoke(query)
        if not docs:
            return "No relevant policies found."
        
        formatted_docs = []
        for doc in docs:
            source = doc.metadata.get('source', 'Unknown Document')
            formatted_docs.append(f"Source: {source}\nExcerpt: {doc.page_content}")
        return "\n\n".join(formatted_docs)

# 3. Instantiate our custom tool so we can pass it to the agent
policy_search_tool = PolicySearchTool()

# 4. Define the main execution function
def run_resolution_crew(ticket_text: str, order_context: dict):
    agents = ResolutionAgents()
    tasks = ResolutionTasks()

    # Instantiate the agents
    triage_agent = agents.triage_agent()
    retriever_agent = agents.policy_retriever_agent(policy_search_tool)
    writer_agent = agents.resolution_writer_agent()
    compliance_agent = agents.compliance_agent()

    # Instantiate the tasks with the ticket data
    triage_task = tasks.triage_task(triage_agent, ticket_text, order_context)
    retrieval_task = tasks.retrieval_task(retriever_agent, ticket_text)
    drafting_task = tasks.drafting_task(writer_agent, ticket_text, order_context)
    compliance_task = tasks.compliance_task(compliance_agent)

    # Form the Crew and set them to work sequentially
    crew = Crew(
        agents=[triage_agent, retriever_agent, writer_agent, compliance_agent],
        tasks=[triage_task, retrieval_task, drafting_task, compliance_task],
        process=Process.sequential,
        verbose=True # This will print the agents' thought processes to your terminal
    )

    result = crew.kickoff()
    return result

if __name__ == "__main__":
    # 5. Define a Test Case (Testing the "Hygiene Exception" policy we wrote earlier)
    sample_ticket = "I bought some earrings last week but they don't match my dress. I opened them but haven't worn them. I want a refund."
    
    # Structured JSON context as required by the assessment
    sample_context = {
        "order_date": "2026-03-20",
        "delivery_date": "2026-03-23",
        "item_category": "apparel_accessories",
        "fulfillment_type": "first-party",
        "shipping_region": "US",
        "order_status": "delivered"
    }

    print("Starting E-Commerce Support Resolution Crew...\n")
    final_output = run_resolution_crew(sample_ticket, sample_context)

    print("\n================================================")
    print("FINAL STRUCTURED OUTPUT:")
    print("================================================")
    print(final_output)