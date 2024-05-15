from streamlit.runtime.scriptrunner.script_run_context import get_script_run_ctx
from streamlit.runtime.scriptrunner import add_script_run_ctx
from dotenv import load_dotenv
import plotly.express as px
import streamlit as st
import pandas as pd
import numpy as np
import threading
import socket
import time
import os

load_dotenv()

HOST = os.getenv('HOST')
PORT = int(os.getenv('PORT'))


temp = pd.DataFrame(columns=['Temperature', 'Timestamp'])
heat = pd.DataFrame(columns=['Heat Flow', 'Timestamp'])
ref_temp = None

def send_message(sock, message):
    sock.sendall(message.encode())
            
def receive_message(sock):
    global temperatures, timestamps, REF_TEMPERATURE
    while True:
        data = sock.recv(1024)
        with open('./files/historiador.txt', 'a') as file:
            file.write(data.decode() + '\n')

def plot(sock):
        
        st.set_page_config(layout="wide")
        st.title("Temperature Control System Dashboard")

        grafico_placeholder = st.empty()
        st.sidebar.title("Control Panel")

        ref_temp = st.sidebar.number_input("Reference Temperature (K)")
        st.sidebar.button("Set", on_click=send_message, args=(sock, f'REF_TEMPERATURE,{ref_temp}'), key='ref_temp')

        kp = st.sidebar.number_input("KP")
        st.sidebar.button("Set", on_click=send_message, args=(sock, f'KP,{kp}'), key='kp')

        ki = st.sidebar.number_input("Constante Integrativa")
        st.sidebar.button("Set", on_click=send_message, args=(sock, f'KI,{ki}'), key='ki')

        kd = st.sidebar.number_input("Constate Derivativa")
        st.sidebar.button("Set", on_click=send_message, args=(sock, f'KD,{kd}'), key='kd')


        def upload_data():
            global temp, heat, ref_temp
            with open('files/historiador.txt', 'r') as file:
                total_linhas = sum(1 for line in file)
            
            linhas_a_pular = total_linhas - 500

            df = pd.read_csv('files/historiador.txt', skiprows=range(1, linhas_a_pular), sep=',', encoding='utf-8', on_bad_lines='skip', usecols=[0, 1, 2])

            df.columns = ['Node', 'Value', 'Time']

            temp = df[df['Node'] == 'TEMPERATURE']
            temp = temp.drop(columns=['Node'])
            temp.columns = ['Temperature', 'Time']

            heat = df[df['Node'] == 'HEAT_FLOW']
            heat = heat.drop(columns=['Node'])
            heat.columns = ['Heat Flow', 'Time']

            if len(df[df['Node'] == 'REF_TEMPERATURE']) > 0:
                ref_temp = df[df['Node'] == 'REF_TEMPERATURE']['Value'].values[0]
            else:
                ref_temp = None


        while True:
            upload_data()
            with grafico_placeholder.container():
                if len(temp) and len(heat) > 0:
                    
                    last_temp = st.empty()
                    heat_flow = st.empty()
                    
                    last_temp.metric("Current Temperature", f'{np.round(temp["Temperature"].tail(1).values[0], 2)} K')
                    heat_flow.metric("Current Heat Flow", f'{np.round(heat["Heat Flow"].tail(1).values[0], 2)} W')

                    pl1, pl2 = st.columns(2)
                    
                    pl1.plotly_chart(px.line(temp, x='Time', y='Temperature', title='Temperature x Time'), use_container_width=True)
                    pl2.plotly_chart(px.line(heat, x='Time', y='Heat Flow', title='Heat Flow x Time'), use_container_width=True)

            time.sleep(1)
if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        
        s.connect((HOST, PORT))
        
        receive_thread = threading.Thread(target=receive_message, args=(s,))
        receive_thread.start()
        
        plot_t = threading.Thread(target=plot, args=(s,))
        ctx = get_script_run_ctx()
        add_script_run_ctx(plot_t)
        plot_t.start()


        receive_thread.join()
        plot_t.join()
