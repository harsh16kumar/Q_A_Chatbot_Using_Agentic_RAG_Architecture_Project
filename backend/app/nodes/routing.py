def check_cgpa(state):
    print("---CHECKING CGPA FOR EMAIL ALERT---")
    if state.get("ug_cgpa", 0) > 9.0:
        print("CGPA > 9 — routing to send_email")
        return {**state, "route": "send_email"}
    else:
        print("CGPA <= 9 — proceeding to generate")
        return {**state, "route": "generate"}
