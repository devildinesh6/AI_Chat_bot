import chainlit as cl
import pandas as pd
import io
import os

# IMPORTS
import ai_chat       
import ai_summarizer 
import db_handler

@cl.on_chat_start
async def start():
    # ---------------------------------------------------------
    # 1. SETUP (Avatars Removed to fix Error)
    # ---------------------------------------------------------
    # In the new Chainlit, we don't set avatars here.
    # (See instructions below on how to add them via folders)

    # ---------------------------------------------------------
    # 2. RESTORE HISTORY
    # ---------------------------------------------------------
    past_chats = db_handler.get_recent_chats(limit=10)
    memory_string = ""
    
    if past_chats:
        await cl.Message(content="📜 **Previous Conversation History:**", author="System").send()
        
        for chat in past_chats:
            user_msg = chat.get("input_text", "")
            bot_msg = chat.get("ai_summary", "")
            
            # Build Memory
            memory_string += f"User: {user_msg}\nAssistant: {bot_msg}\n"
            
            # Draw to UI
            await cl.Message(content=user_msg, author="User").send()
            await cl.Message(content=bot_msg, author="Copilot").send()
            
        await cl.Message(content="--- *End of History* ---", author="System").send()
            
    # Save memory to session
    cl.user_session.set("chat_history", memory_string)
    
    await cl.Message(content="👋 **I am Ready!**", author="Copilot").send()

@cl.on_message
async def main(message: cl.Message):
    
    # PATH A: TEXT CHAT
    if not message.elements:
        user_text = message.content
        msg = cl.Message(content="Thinking...", author="Copilot")
        await msg.send()

        current_history = cl.user_session.get("chat_history", "")

        # Call Chat Brain
        response = await cl.make_async(ai_chat.get_response)(user_text, current_history)
        
        # Save & Update
        db_handler.save_log("Chat_Mode", user_text, response)
        new_entry = f"User: {user_text}\nAssistant: {response}\n"
        cl.user_session.set("chat_history", current_history + new_entry)

        msg.content = response
        await msg.update()
        return 

    # PATH B: EXCEL FILE
    excel_file = None
    file_name = "Unknown"
    
    for element in message.elements:
        if element.name.lower().endswith(".xlsx") or "excel" in element.mime:
            excel_file = element.path
            file_name = element.name
            break
    
    if not excel_file:
        await cl.Message(content="❌ Please upload a file ending in .xlsx", author="Copilot").send()
        return

    msg = cl.Message(content=f"📂 Reading **{file_name}**...", author="Copilot")
    await msg.send()

    try:
        df = pd.read_excel(excel_file)
        if "Description" not in df.columns:
            msg.content = "❌ Column 'Description' is missing."
            await msg.update()
            return

        summaries = []
        total_rows = len(df)
        
        async with cl.Step(name="AI Processing", type="run") as step:
            step.input = f"Summarizing {total_rows} rows..."
            for index, row in df.iterrows():
                text = str(row["Description"])
                summary = await cl.make_async(ai_summarizer.generate_summary)(text)
                summaries.append(summary)
                db_handler.save_log(file_name, text, summary)
                step.name = f"Processing ({index + 1}/{total_rows})"
                await step.update()
            step.output = "Done!"

        # Download Logic
        base_name = os.path.splitext(file_name)[0]
        output_name = f"{base_name}_summarized.xlsx"
        df["short_paraphrase"] = summaries
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        buffer.seek(0)
        
        await cl.Message(
            content=f"✅ **Done!**",
            elements=[
                cl.File(name=output_name, content=buffer.getvalue(), mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            ],
            author="Copilot"
        ).send()

    except Exception as e:
        await cl.Message(content=f"❌ Error: {str(e)}", author="Copilot").send()