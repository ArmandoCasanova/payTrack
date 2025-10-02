def new_user_verification_code_email_tempalte(
    user_name: str,
    code: int,
) -> str:
    head = """
        <!DOCTYPE html>
            <html lang="en">
            <head>
                
            </head>
    """

    body = f"""
        <body style="margin:0; padding:0; background-color:#fff; font-family: sans-serif;">
            
        </body>
        </html>
    """

    return f"{head}{body}"
