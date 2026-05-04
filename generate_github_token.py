"""
generate_github_token.py
YouTube token ko base64 mein convert karo GitHub Secrets ke liye
"""
import base64, os

token_file = "assets/youtube_token.pkl"

if not os.path.exists(token_file):
    print("❌ YouTube token nahi mila!")
    print("Pehle python manual_workflow.py chalao aur YouTube authenticate karo")
else:
    with open(token_file, 'rb') as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    print("\n✅ YouTube Token (GitHub Secret mein daalo):")
    print("="*60)
    print(b64)
    print("="*60)
    print("\nGitHub → Settings → Secrets → YOUTUBE_TOKEN mein paste karo")

# client_secrets.json bhi
cs_file = "client_secrets.json"
if os.path.exists(cs_file):
    with open(cs_file, 'rb') as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    print("\n✅ Client Secrets (GitHub Secret mein daalo):")
    print("="*60)
    print(b64)
    print("="*60)
    print("\nGitHub → Settings → Secrets → CLIENT_SECRETS mein paste karo")
