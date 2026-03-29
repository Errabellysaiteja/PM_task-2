import json
import time
from main import run_resolution_crew

# Define the 20 Evaluation Test Cases
test_cases = [
    # --- 8 STANDARD CASES (Normal returns, shipping inquiries) ---
    {"type": "standard", "ticket": "I want to return this shirt. It doesn't fit.", "context": {"order_date": "2026-03-20", "delivery_date": "2026-03-25", "item_category": "apparel", "fulfillment_type": "first-party", "shipping_region": "US", "order_status": "delivered"}},
    {"type": "standard", "ticket": "Where is my order? It was supposed to be here yesterday.", "context": {"order_date": "2026-03-22", "delivery_date": None, "item_category": "electronics", "fulfillment_type": "first-party", "shipping_region": "US", "order_status": "shipped"}},
    {"type": "standard", "ticket": "I need to cancel my order immediately. I just placed it 10 minutes ago.", "context": {"order_date": "2026-03-29", "delivery_date": None, "item_category": "home", "fulfillment_type": "first-party", "shipping_region": "US", "order_status": "placed"}},
    {"type": "standard", "ticket": "My package arrived but the lamp is completely shattered.", "context": {"order_date": "2026-03-20", "delivery_date": "2026-03-28", "item_category": "home", "fulfillment_type": "first-party", "shipping_region": "US", "order_status": "delivered"}},
    {"type": "standard", "ticket": "Can I use two coupons on my next order?", "context": {"order_date": None, "delivery_date": None, "item_category": "general", "fulfillment_type": "first-party", "shipping_region": "US", "order_status": "none"}},
    {"type": "standard", "ticket": "The tracking hasn't updated in 8 days. I think my package is lost.", "context": {"order_date": "2026-03-15", "delivery_date": None, "item_category": "apparel", "fulfillment_type": "first-party", "shipping_region": "US", "order_status": "shipped"}},
    {"type": "standard", "ticket": "I want to return these shoes, they are still in the unopened box.", "context": {"order_date": "2026-03-10", "delivery_date": "2026-03-15", "item_category": "footwear", "fulfillment_type": "first-party", "shipping_region": "US", "order_status": "delivered"}},
    {"type": "standard", "ticket": "Why doesn't my SAVE20 coupon work on this $50 order?", "context": {"order_date": None, "delivery_date": None, "item_category": "general", "fulfillment_type": "first-party", "shipping_region": "US", "order_status": "none"}},

    # --- 6 EXCEPTION-HEAVY CASES (Hygiene, perishables, final sale) ---
    {"type": "exception", "ticket": "I opened these headphones but don't like the sound. Can I return them?", "context": {"order_date": "2026-03-20", "delivery_date": "2026-03-22", "item_category": "electronics", "fulfillment_type": "first-party", "shipping_region": "US", "order_status": "delivered"}},
    {"type": "exception", "ticket": "I bought this swimsuit on Final Sale but it's too small.", "context": {"order_date": "2026-03-20", "delivery_date": "2026-03-25", "item_category": "apparel", "fulfillment_type": "first-party", "shipping_region": "US", "order_status": "delivered"}},
    {"type": "exception", "ticket": "The chocolates I ordered arrived completely melted into a puddle.", "context": {"order_date": "2026-03-25", "delivery_date": "2026-03-28", "item_category": "perishable", "fulfillment_type": "first-party", "shipping_region": "US", "order_status": "delivered"}},
    {"type": "exception", "ticket": "I tried on this underwear but it doesn't fit right. Need a refund.", "context": {"order_date": "2026-03-15", "delivery_date": "2026-03-20", "item_category": "hygiene", "fulfillment_type": "first-party", "shipping_region": "US", "order_status": "delivered"}},
    {"type": "exception", "ticket": "I opened the video game, played it for an hour, but it's boring. Refund please.", "context": {"order_date": "2026-03-20", "delivery_date": "2026-03-24", "item_category": "software", "fulfillment_type": "first-party", "shipping_region": "US", "order_status": "delivered"}},
    {"type": "exception", "ticket": "Cancel my custom engraved watch order. I ordered it 3 hours ago.", "context": {"order_date": "2026-03-29", "delivery_date": None, "item_category": "custom", "fulfillment_type": "first-party", "shipping_region": "US", "order_status": "processing"}},

    # --- 3 CONFLICT CASES (Region vs Standard, Marketplace vs Standard) ---
    {"type": "conflict", "ticket": "I want to return this jacket. I know it's past 30 days, but I live in London.", "context": {"order_date": "2026-02-10", "delivery_date": "2026-02-15", "item_category": "apparel", "fulfillment_type": "first-party", "shipping_region": "UK", "order_status": "delivered"}},
    {"type": "conflict", "ticket": "I want to return this camera I bought from a third-party seller on your site.", "context": {"order_date": "2026-03-20", "delivery_date": "2026-03-25", "item_category": "electronics", "fulfillment_type": "marketplace", "shipping_region": "US", "order_status": "delivered"}},
    {"type": "conflict", "ticket": "My EU order took 6 days to arrive instead of standard 3-5 days. I want to withdraw from the purchase.", "context": {"order_date": "2026-03-10", "delivery_date": "2026-03-16", "item_category": "general", "fulfillment_type": "first-party", "shipping_region": "EU", "order_status": "delivered"}},

    # --- 3 NOT-IN-POLICY CASES (Price match, out of scope requests) ---
    {"type": "not_in_policy", "ticket": "I found this exact same TV at Best Buy for $50 cheaper. Will you price match?", "context": {"order_date": "2026-03-28", "delivery_date": None, "item_category": "electronics", "fulfillment_type": "first-party", "shipping_region": "US", "order_status": "shipped"}},
    {"type": "not_in_policy", "ticket": "Do you offer a military discount for active duty service members?", "context": {"order_date": None, "delivery_date": None, "item_category": "general", "fulfillment_type": "first-party", "shipping_region": "US", "order_status": "none"}},
    {"type": "not_in_policy", "ticket": "Can I trade in my old laptop for store credit towards a new one?", "context": {"order_date": None, "delivery_date": None, "item_category": "electronics", "fulfillment_type": "first-party", "shipping_region": "US", "order_status": "none"}}
]

def run_evaluation():
    results = []
    print(f"Starting Evaluation of {len(test_cases)} tickets...\n")
    
    for i, case in enumerate(test_cases):
        print(f"--- Running Case {i+1}/{len(test_cases)}: {case['type'].upper()} ---")
        print(f"Ticket: {case['ticket']}")
        
        try:
            # Run the agent crew
            output = run_resolution_crew(case['ticket'], case['context'])
            
            # Since CrewAI's output is an object, we cast it to string, but ideally it returns JSON based on our task
            output_str = str(output)
            
            result_record = {
                "case_id": i + 1,
                "type": case['type'],
                "ticket": case['ticket'],
                "agent_output": output_str
            }
            results.append(result_record)
            print("Successfully processed.\n")
            
        except Exception as e:
            print(f"Error processing case {i+1}: {e}\n")
            results.append({"case_id": i + 1, "type": case['type'], "error": str(e)})
            
        # Optional: Sleep for 5 seconds to avoid hitting Gemini free tier rate limits
        time.sleep(5) 

    # Save to a file for analysis
    output_file = "evaluation_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=4)
        
    print(f"\nEvaluation Complete! Results saved to {output_file}")

if __name__ == "__main__":
    run_evaluation()