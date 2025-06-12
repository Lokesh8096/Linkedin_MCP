import streamlit as st
import requests

def post_to_linkedin(text):
    access_token = st.secrets["linkedin"]["access_token"]
    person_urn = st.secrets["linkedin"]["person_urn"]

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }

    body = {
        "author": person_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text},
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    return requests.post("https://api.linkedin.com/v2/ugcPosts", headers=headers, json=body)