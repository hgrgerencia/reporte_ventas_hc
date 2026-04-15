import streamlit as st

def try_except_decorator(function):
    def wrapper(*args, **kwargs):
        try:
            result = function(*args, **kwargs)
            return result
        except Exception as e:
            st.toast(f"Mensaje de Error: {e}", icon="⚠️")
            return [[],[]]
    return wrapper

def try_except_decorator_view(function):
    def wrapper(*args, **kwargs):
        try:
            function(*args, **kwargs)
        except Exception as e:
            st.toast(f"Mensaje de Error: {e}", icon="⚠️")
    return wrapper