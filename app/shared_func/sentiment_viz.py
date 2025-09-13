import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st

def create_sentiment_pie(df):
    """Create pie chart showing sentiment distribution"""
    if 'sentiment_score' not in df.columns:
        return None
    
    # Create sentiment level categories
    df_viz = df.copy()
    df_viz['sentiment_level'] = pd.cut(
        df_viz['sentiment_score'], 
        bins=[0, 0.33, 0.66, 1.0], 
        labels=['😞 Negative', '😐 Neutral', '😊 Positive'],
        include_lowest=True
    )
    
    # Count by sentiment level
    sentiment_counts = df_viz['sentiment_level'].value_counts()
    
    # Create pie chart
    fig = px.pie(
        values=sentiment_counts.values,
        names=sentiment_counts.index,
        color=sentiment_counts.index,
        color_discrete_map={
            '😞 Negative': '#ff4444',
            '😐 Neutral': '#ffaa00', 
            '😊 Positive': '#44ff44'
        },
        height=300
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(showlegend=False)
    
    return fig

def create_sentiment_counts(df):
    """Create bar chart showing counts of sentiment groups"""
    if 'sentiment_score' not in df.columns:
        return None
    
    # Count sentiment groups
    negative_low_count = len(df[df['sentiment_score'] <= 0.1])
    positive_count = len(df[df['sentiment_score'] > 0.1])
    
    fig = go.Figure(data=[
        go.Bar(
            x=['Negative/Low (≤0.1)', 'Positive or Neutral (>0.1)'],
            y=[negative_low_count, positive_count],
            marker_color=['red', 'green'],
            text=[negative_low_count, positive_count],
            textposition='auto'
        )
    ])
    
    fig.update_layout(
        title='Sentiment Group Counts',
        xaxis_title='Sentiment Groups',
        yaxis_title='Number of Comments',
        height=400
    )
    
    return fig

def create_sentiment_combined(df):
    """Create combined pie and box chart showing sentiment analysis"""
    if 'sentiment_score' not in df.columns:
        return None
    
    from plotly.subplots import make_subplots
    
    # Create sentiment level categories
    df_viz = df.copy()
    df_viz['sentiment_level'] = pd.cut(
        df_viz['sentiment_score'], 
        bins=[0, 0.33, 0.66, 1.0], 
        labels=['😞 Negative', '😐 Neutral', '😊 Positive'],
        include_lowest=True
    )
    
    # Count by sentiment level
    sentiment_counts = df_viz['sentiment_level'].value_counts()
    
    # Create subplots
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "pie"}, {"type": "box"}]],
        subplot_titles=('Distribution', 'Score Range')
    )
    
    # Pie chart
    fig.add_trace(
        go.Pie(
            labels=sentiment_counts.index,
            values=sentiment_counts.values,
            marker_colors=['#ff4444', '#ffaa00', '#44ff44'],
            textinfo='percent+label',
            textposition='inside'
        ),
        row=1, col=1
    )
    
    # Box plot - divided into meaningful threat analysis groups
    negative_scores = df[df['sentiment_score'] <= 0.1]['sentiment_score']  # Negative + low neutral (potential threats)
    positive_scores = df[df['sentiment_score'] > 0.1]['sentiment_score']   # Clearly positive (likely safe)
    
    # Add negative/low sentiment box (potential threats)
    fig.add_trace(
        go.Box(
            y=negative_scores,
            name='Negative/Low',
            marker_color='red',
            showlegend=False
        ),
        row=1, col=2
    )
    
    # Add positive sentiment box (likely safe)
    fig.add_trace(
        go.Box(
            y=positive_scores,
            name='Positive or Neutral',
            marker_color='green',
            showlegend=False
        ),
        row=1, col=2
    )
    
    fig.update_layout(height=400, showlegend=False)
    
    return fig
