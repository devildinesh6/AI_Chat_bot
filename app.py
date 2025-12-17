import chainlit as cl
import pandas as pd
import io

# IMPORTS
import ai_chat       
import ai_summarizer 
import db_handler

@cl.on_chat_start
async def start():
    await cl.Message(
        content="👋 **Ready!**\n\n- **Chat:** Just type.\n- **Work:** Drop an Excel file.",
        author="Copilot"
    ).send()

@cl.on_message
async def main(message: cl.Message):
    
    # ==========================================
    # PATH A: TEXT CHAT
    # ==========================================
    if not message.elements:
        user_text = message.content
        msg = cl.Message(content="Thinking...", author="Copilot")
        await msg.send()

        # UPDATED: Use make_async to prevent freezing during chat
        response = await cl.make_async(ai_chat.get_response)(user_text)
        
        db_handler.save_log("Chat_Mode", user_text, response)

        msg.content = response
        await msg.update()
        return 

    # ==========================================
    # PATH B: EXCEL FILE
    # ==========================================
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
                
                # ---------------------------------------------------------
                # ✅ THE FIX: Run in background thread using make_async
                # ---------------------------------------------------------
                summary = await cl.make_async(ai_summarizer.generate_summary)(text)
                
                summaries.append(summary)
                db_handler.save_log(file_name, text, summary)

                # Update UI more frequently (every row) to keep connection alive
                step.name = f"Processing ({index + 1}/{total_rows})"
                await step.update()
            
            step.output = "Done!"

        # Download Logic
        df["short_paraphrase"] = summaries
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        buffer.seek(0)
        
        await cl.Message(
            content="✅ **Done!**",
            elements=[
                cl.File(name="output.xlsx", content=buffer.getvalue(), mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            ],
            author="Copilot"
        ).send()

    except Exception as e:
        await cl.Message(content=f"❌ Error: {str(e)}", author="Copilot").send()