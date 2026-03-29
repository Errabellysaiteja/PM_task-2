import os
from crewai import Agent
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

class ResolutionAgents:
    def __init__(self):
        # We now pass the model name as a string using the LiteLLM format expected by CrewAI.
        # CrewAI will automatically look for the GEMINI_API_KEY in your environment.
        self.llm_string = "gemini/gemini-2.5-flash"

    def triage_agent(self):
        return Agent(
            role='Customer Support Triage Specialist',
            goal='Classify incoming e-commerce support tickets and identify any missing required information.',
            backstory=(
                "You are the first line of defense in a busy e-commerce support team. "
                "Your job is to read customer tickets, look at the structured order context (JSON), "
                "and classify the exact issue type (e.g., refund, shipping, promo). "
                "If critical details are missing to resolve the issue, you formulate clarifying questions."
            ),
            verbose=True,
            allow_delegation=False,
            llm=self.llm_string
        )

    def policy_retriever_agent(self, search_tool):
        return Agent(
            role='Policy Knowledge Expert',
            goal='Retrieve the exact, relevant policy clauses and strictly provide citations for a given issue.',
            backstory=(
                "You are a strict, meticulous policy librarian. You do not invent answers. "
                "You use the provided search tool to query the company vector database. "
                "You extract only the exact text relevant to the customer's issue and you ALWAYS "
                "attach the source document name as a citation. If the policy doesn't cover it, you state that clearly."
            ),
            tools=[search_tool],
            verbose=True,
            allow_delegation=False,
            llm=self.llm_string
        )

    def resolution_writer_agent(self):
        return Agent(
            role='Customer Resolution Writer',
            goal='Draft a highly professional, empathetic customer response using ONLY retrieved policy evidence.',
            backstory=(
                "You are a senior customer support communicator. "
                "You take the classification from the Triage Agent and the precise policies from the "
                "Policy Retriever Agent, and you draft a resolution. You NEVER make unsupported claims. "
                "You must base your decision (approve/deny/escalate) strictly on the provided policy context."
            ),
            verbose=True,
            allow_delegation=False,
            llm=self.llm_string
        )

    def compliance_agent(self):
        return Agent(
            role='Compliance and Safety Auditor',
            goal='Audit the final resolution for policy accuracy, mandatory citations, and safe language.',
            backstory=(
                "You are the final quality assurance checkpoint. You review the drafted customer resolution. "
                "You check for three things: 1) Are there unsupported statements? 2) Are citations missing? "
                "3) Does it violate exception policies (like hygiene items or final sale)? "
                "If it fails any check, you correct it or flag it as 'needs escalation'."
            ),
            verbose=True,
            allow_delegation=False,
            llm=self.llm_string
        )