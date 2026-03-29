from crewai import Task
from pydantic import BaseModel, Field
from typing import List

# 1. Define the Expected Output Structures (Data Contracts)
class TicketClassification(BaseModel):
    issue_type: str = Field(description="The category of the issue (e.g., refund, shipping, exception)")
    confidence: float = Field(description="Confidence score from 0.0 to 1.0")
    missing_info: bool = Field(description="True if critical order context is missing")
    clarifying_questions: List[str] = Field(description="Max 3 questions to ask the customer if info is missing", max_length=3)

class RetrievedPolicy(BaseModel):
    relevant_excerpts: List[str] = Field(description="Exact quotes from the policy")
    citations: List[str] = Field(description="Bullet list with document title and section/chunk id")
    policy_covers_issue: bool = Field(description="True if the policy explicitly covers the customer request")

class DraftedResolution(BaseModel):
    decision: str = Field(description="Must be one of: approve, deny, partial, needs escalation")
    rationale: str = Field(description="Internal policy-based explanation for the decision")
    customer_response_draft: str = Field(description="The customer-ready message")

class FinalOutput(BaseModel):
    classification: str = Field(description="Issue type and confidence")
    clarifying_questions: List[str] = Field(description="List of questions if needed")
    decision: str = Field(description="approve/deny/partial/needs escalation")
    rationale: str = Field(description="Policy-based explanation")
    citations: List[str] = Field(description="Bullet list of citations backing the decision")
    customer_response_draft: str = Field(description="Customer-ready message")
    next_steps: str = Field(description="What the agent recommends support does next")

# 2. Define the Tasks for the Agents
class ResolutionTasks:
    def triage_task(self, agent, ticket_text, order_context):
        return Task(
            description=(
                f"Analyze the following support ticket and order context.\n\n"
                f"Ticket: {ticket_text}\n"
                f"Context: {order_context}\n\n"
                f"Classify the issue and determine if any information is missing. "
                f"If information is missing, formulate up to 3 clarifying questions."
            ),
            expected_output="A structured classification of the ticket.",
            agent=agent,
            output_json=TicketClassification
        )

    def retrieval_task(self, agent, ticket_text):
        return Task(
            description=(
                f"Search the policy database to find rules governing this issue: '{ticket_text}'. "
                f"Extract the exact text and format the citations clearly."
            ),
            expected_output="Relevant policy excerpts with mandatory citations.",
            agent=agent,
            output_json=RetrievedPolicy
        )

    def drafting_task(self, agent, ticket_text, order_context):
        return Task(
            description=(
                f"Draft a resolution for this ticket: '{ticket_text}' (Context: {order_context}). "
                f"You MUST use the policy excerpts provided by the Retriever Agent. "
                f"Determine the decision (approve/deny/escalate) and write a customer-facing draft."
            ),
            expected_output="A structured resolution draft including the decision and rationale.",
            agent=agent,
            output_json=DraftedResolution
        )

    def compliance_task(self, agent):
        return Task(
            description=(
                "Review the drafted resolution, the retrieved policies, and the triage data. "
                "Ensure every claim in the rationale and customer response is backed by a citation. "
                "Ensure no sensitive data is leaked and exception policies are strictly followed. "
                "Compile the final structured output."
            ),
            expected_output="The final, audited, structured JSON output ready for the support team.",
            agent=agent,
            output_json=FinalOutput
        )