import time
from openai import OpenAI

# Zet hier je eigen OpenAI API key
client = OpenAI(api_key="secret")

num_tests = 10
latencies = []
success_count = 0

print("Start API-latency test...")

for i in range(num_tests):
    start = time.time()
    try:
        # Nieuwe interface voor chat completion
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Zeg hallo!"}]
        )
        end = time.time()
        latency = end - start
        latencies.append(latency)
        success_count += 1
        print(f"Call {i+1}: {latency:.2f} sec ✅")
    except Exception as e:
        print(f"Call {i+1}: FOUT ❌ - {e}")

if latencies:
    avg_latency = sum(latencies) / len(latencies)
    print(f"\n✅ Gemiddelde latency: {avg_latency:.2f} sec")
    print(f"✅ Succesratio: {success_count}/{num_tests}")
else:
    print("\n⚠️ Geen succesvolle calls, netwerk mogelijk niet stabiel.")
