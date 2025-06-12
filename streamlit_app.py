import streamlit as st
import requests
import json
import logging
import google.generativeai as genai
from io import BytesIO
import base64
import os

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)

# --- App Configuration ---
st.set_page_config(
    page_title="LinkedIn Post Publisher with AI",
    page_icon="🚀",
    layout="wide"
)

# --- Secure API Key Management ---
def get_api_keys():
    """Securely get API keys from Streamlit secrets or environment variables"""
    try:
        # Try Streamlit secrets first (for Streamlit Cloud)
        gemini_api_key = st.secrets["GOOGLE_API_KEY"]
        linkedin_token = st.secrets["LINKEDIN_ACCESS_TOKEN"]
        return gemini_api_key, linkedin_token
    except (KeyError, FileNotFoundError):
        # Fallback to environment variables
        gemini_api_key = os.getenv("GOOGLE_API_KEY")
        linkedin_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
        return gemini_api_key, linkedin_token

# Get API keys
gemini_api_key, FIXED_ACCESS_TOKEN = get_api_keys()

# Validation
if not gemini_api_key or not FIXED_ACCESS_TOKEN:
    st.error("❌ Please configure your API keys")
    st.info("""
    **For Streamlit Cloud:**
    1. Go to your app settings
    2. Add secrets in TOML format:
    ```
    GOOGLE_API_KEY = "your-gemini-key"
    LINKEDIN_ACCESS_TOKEN = "your-linkedin-token"
    ```
    
    **For Local Development:**
    Create `.streamlit/secrets.toml` with the same format
    """)
    st.stop()

# Configure Gemini API
genai.configure(api_key=gemini_api_key)

# --- App Title and Description ---
st.title("🚀 LinkedIn Post Publisher with AI")
st.write(
    "This app uses Gemini AI to generate professional LinkedIn posts based on your inputs, "
    "then publishes them to your LinkedIn profile with optional images/videos."
)

# --- Main UI Layout ---
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📝 Input Details")
    
    # User inputs
    day_number = st.number_input("Day Number", min_value=1, max_value=365, value=1)
    project_title = st.text_input("Project Title", placeholder="e.g., E-commerce Dashboard")
    
    # Technologies (allow multiple)
    st.write("**Technologies Used:**")
    tech1 = st.text_input("Technology 1", placeholder="e.g., React.js")
    tech2 = st.text_input("Technology 2", placeholder="e.g., Node.js")
    tech3 = st.text_input("Technology 3", placeholder="e.g., MongoDB")
    tech4 = st.text_input("Technology 4 (Optional)", placeholder="e.g., Tailwind CSS")
    
    # Media upload
    st.write("**Media (Optional):**")
    media_type = st.selectbox("Media Type", ["None", "Image", "Video"])
    
    uploaded_file = None
    if media_type == "Image":
        uploaded_file = st.file_uploader(
            "Upload Image", 
            type=['png', 'jpg', 'jpeg', 'gif'],
            help="Supported formats: PNG, JPG, JPEG, GIF (Max 10MB)"
        )
    elif media_type == "Video":
        uploaded_file = st.file_uploader(
            "Upload Video", 
            type=['mp4', 'avi', 'mov', 'wmv'],
            help="Supported formats: MP4, AVI, MOV, WMV (Max 200MB)"
        )
    
    # Additional customization
    with st.expander("🎨 Customize Post"):
        custom_milestone = st.text_input("Custom Milestone (Optional)", placeholder="Built responsive UI components")
        custom_skills = st.text_input("Additional Skills (Optional)", placeholder="State Management, API Integration")
        custom_next_phase = st.text_input("Next Phase (Optional)", placeholder="Backend integration and deployment")

with col2:
    st.header("🤖 AI Generated Post")
    
    # Generate post button
    if st.button("🎯 Generate LinkedIn Post", type="primary"):
        if not project_title or not tech1:
            st.error("❌ Please fill in at least the project title and first technology!")
        else:
            with st.spinner("🤖 Generating post with Gemini AI..."):
                try:
                    # Prepare technologies list
                    technologies = [tech for tech in [tech1, tech2, tech3, tech4] if tech.strip()]
                    tech_string = " • ".join(technologies)
                    
                    # Create prompt for Gemini
                    prompt = f"""
Generate a professional LinkedIn post for a  student at NIAT following this exact format and also don't use "**" in the post:

Day {day_number} |  at NIAT
🎯 Milestone Achieved: [Generate an appropriate milestone based on the project]
🔧 Project Delivered: {project_title}
 [Generate 3 key features/components of this project]
 [Feature 2]  
 [Feature 3]
⚡ Tech Stack: {tech_string}
📊 Skills Gained: [Generate 4 relevant skills based on the technologies and project]
🚀 Next Phase: [Generate next logical step in development journey]

Building industry-ready developers through hands-on project experience.

#NIAT #ReactJS #FrontendDevelopment #WebDev #TechEducation #StudentSuccess

Project Details:
- Day: {day_number}
- Project: {project_title}
- Technologies: {tech_string}
{f"- Custom Milestone: {custom_milestone}" if custom_milestone else ""}
{f"- Additional Skills: {custom_skills}" if custom_skills else ""}
{f"- Next Phase: {custom_next_phase}" if custom_next_phase else ""}

Make it engaging, professional, and inspiring. Focus on growth, learning, and practical experience.
"""

                    # Generate content with Gemini
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(prompt)
                    generated_post = response.text
                    
                    # Store in session state
                    st.session_state.generated_post = generated_post
                    
                    st.success("✅ Post generated successfully!")
                    
                except Exception as e:
                    st.error(f"❌ Error generating post: {str(e)}")
                    st.info("💡 Try using a different model or check your API quota")

    # Display generated post
    if 'generated_post' in st.session_state:
        st.write("**Generated Post:**")
        generated_post_area = st.text_area(
            "Edit if needed:", 
            value=st.session_state.generated_post, 
            height=400,
            key="editable_post"
        )
        
        # Preview uploaded media
        if uploaded_file is not None:
            st.write("**Media Preview:**")
            if media_type == "Image":
                st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
            elif media_type == "Video":
                st.video(uploaded_file)

# --- LinkedIn API Functions ---
def get_user_urn(token):
    """Fetch user URN from LinkedIn API"""
    userinfo_url = "https://api.linkedin.com/v2/userinfo"
    headers = {
        "Authorization": f"Bearer {token.strip()}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(userinfo_url, headers=headers)
        response.raise_for_status()
        userinfo_data = response.json()
        user_name = userinfo_data.get('name', 'N/A')
        user_id = userinfo_data.get("sub")
        return user_id, user_name
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching user info: {e}")
        if response.status_code == 401:
            st.error("❌ LinkedIn token expired or invalid. Please update your token.")
        return None, None

def upload_media_to_linkedin(token, author_urn, file_content, file_type):
    """Upload media to LinkedIn and return media URN"""
    try:
        # Step 1: Register upload
        if file_type.startswith('image'):
            media_category = "IMAGE"
        else:
            media_category = "VIDEO"
            
        register_url = "https://api.linkedin.com/v2/assets?action=registerUpload"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        register_data = {
            "registerUploadRequest": {
                "recipes": [f"urn:li:digitalmediaRecipe:feedshare-{media_category.lower()}"],
                "owner": f"urn:li:person:{author_urn}",
                "serviceRelationships": [
                    {
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent"
                    }
                ]
            }
        }
        
        response = requests.post(register_url, headers=headers, json=register_data)
        response.raise_for_status()
        register_response = response.json()
        
        # Step 2: Upload the actual file
        upload_mechanism = register_response['value']['uploadMechanism']
        upload_url = upload_mechanism['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']
        asset_id = register_response['value']['asset']
        
        # Upload file
        upload_headers = {"Authorization": f"Bearer {token}"}
        upload_response = requests.post(upload_url, headers=upload_headers, data=file_content)
        upload_response.raise_for_status()
        
        return asset_id
        
    except Exception as e:
        st.error(f"Error uploading media: {e}")
        return None

def create_linkedin_post_with_media(author_urn, text, token, media_urn=None, media_type="IMAGE"):
    """Create LinkedIn post with optional media"""
    post_url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {token.strip()}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }
    
    # Base post data
    post_data = {
        "author": f"urn:li:person:{author_urn}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": text
                },
                "shareMediaCategory": "NONE" if not media_urn else media_type
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }
    
    # Add media if available
    if media_urn:
        media_title = "Project Video" if media_type == "VIDEO" else "Project Image"
        post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [
            {
                "status": "READY",
                "description": {
                    "text": "Project showcase"
                },
                "media": media_urn,
                "title": {
                    "text": media_title
                }
            }
        ]
        post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = media_type
    
    try:
        response = requests.post(post_url, headers=headers, json=post_data)
        response.raise_for_status()
        return True, response.json()
    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        if response.status_code == 401:
            error_msg = "LinkedIn token expired or invalid"
        elif response.status_code == 403:
            error_msg = "Insufficient permissions. Check your LinkedIn app scopes"
        return False, error_msg

# --- Publish Section ---
st.header("📤 Publish to LinkedIn")

col1, col2 = st.columns(2)

with col1:
    if st.button("🚀 Publish Post", type="primary"):
        if 'generated_post' not in st.session_state:
            st.error("❌ Please generate a post first!")
        else:
            with st.spinner("📤 Publishing to LinkedIn..."):
                # Get user info
                user_id, user_name = get_user_urn(FIXED_ACCESS_TOKEN)
                
                if user_id:
                    st.info(f"👤 Posting as: {user_name}")
                    
                    media_urn = None
                    
                    # Upload media if provided
                    if uploaded_file is not None:
                        st.info("⬆️ Uploading media...")
                        file_content = uploaded_file.read()
                        file_type = uploaded_file.type
                        media_urn = upload_media_to_linkedin(FIXED_ACCESS_TOKEN, user_id, file_content, file_type)
                        
                        if media_urn:
                            st.success("✅ Media uploaded successfully!")
                        else:
                            st.warning("⚠️ Media upload failed, posting without media...")
                    
                    # Determine media category for LinkedIn API
                    linkedin_media_type = None
                    if uploaded_file is not None and media_urn:
                        if uploaded_file.type.startswith('image'):
                            linkedin_media_type = "IMAGE"
                        elif uploaded_file.type.startswith('video'):
                            linkedin_media_type = "VIDEO"
                    
                    # Create post
                    success, result = create_linkedin_post_with_media(
                        user_id, 
                        st.session_state.editable_post, 
                        FIXED_ACCESS_TOKEN, 
                        media_urn,
                        linkedin_media_type
                    )
                    
                    if success:
                        st.success("🎉 Post published successfully to LinkedIn!")
                        st.balloons()
                        with st.expander("📊 Response Details"):
                            st.json(result)
                    else:
                        st.error(f"❌ Failed to publish post: {result}")

with col2:
    if st.button("🔄 Clear & Start Over"):
        # Clear all session state
        keys_to_clear = ['generated_post', 'editable_post']
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

# --- Status & Info Section ---
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("🔑 API Status", "✅ Connected" if gemini_api_key else "❌ Missing")

with col2:
    st.metric("🔗 LinkedIn", "✅ Configured" if FIXED_ACCESS_TOKEN else "❌ Missing")

with col3:
    if 'generated_post' in st.session_state:
        post_length = len(st.session_state.generated_post)
        st.metric("📝 Post Length", f"{post_length} chars")

# --- Footer ---
st.markdown("---")
st.markdown("""
### 🎯 Features:
- ✅ AI-powered post generation with Gemini
- ✅ Professional NIAT template format
- ✅ Image and video support
- ✅ Customizable content
- ✅ Direct LinkedIn publishing
- ✅ Secure API key management

### 📋 Setup Guide:
1. **Get API Keys**: Gemini API from [Google AI Studio](https://makersuite.google.com/)
2. **LinkedIn Token**: From LinkedIn Developer Console
3. **Deploy**: Push to GitHub and deploy on Streamlit Cloud
4. **Configure Secrets**: Add your API keys in app settings

**Need help?** Check the README.md in the repository.
""")

# --- Debug Panel (only in development) ---
if st.checkbox("🐛 Debug Panel", help="Show debug information"):
    st.subheader("Debug Information")
    st.write("**Environment:**")
    st.write(f"- Python: {st.__version__}")
    st.write(f"- Streamlit: {st.__version__}")
    
    if 'generated_post' in st.session_state:
        st.write("**Session State:**")
        st.write(f"- Generated post: {len(st.session_state.generated_post)} characters")
        
    st.write("**File Upload Info:**")
    if uploaded_file:
        st.write(f"- File name: {uploaded_file.name}")
        st.write(f"- File type: {uploaded_file.type}")
        st.write(f"- File size: {uploaded_file.size} bytes")
