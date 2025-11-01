import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import webbrowser


def plot_actual_vs_predicted_single(csv_path, out_html='geoplot_actual_vs_pred.html', sample=None, open_in_browser=False):
    """
    Read a single CSV containing the columns:
      LATITUDE, LONGITUDE, Actual_Sound_Speed, Predicted_Sound_Speed

    Plot both actual and predicted sound speed as overlaid Scattergeo traces.
    Writes an interactive HTML file to out_html. Optionally opens it in the default browser.
    """
    p = Path(csv_path)
    if not p.exists():
        raise FileNotFoundError(f"CSV not found: {p}")

    df = pd.read_csv(p)

    # Optionally sample for performance
    if sample is not None and sample > 0 and len(df) > sample:
        df_act = df.sample(n=sample, random_state=1)
    else:
        df_act = df

    # Build figure
    fig = go.Figure()

    # Actual sound speed trace
    fig.add_trace(go.Scattergeo(
        lat=df_act['LATITUDE'],
        lon=df_act['LONGITUDE'],
        mode='markers',
        name='Actual Sound Speed',
        marker=dict(
            size=4,
            color=df_act['Actual_Sound_Speed'],
            colorscale='Viridis',
            # colorbar=dict(title='Actual (m/s)'),
            cmin=df_act['Actual_Sound_Speed'].min(),
            cmax=df_act['Actual_Sound_Speed'].max(),
            opacity=0.8
        ),
        hovertemplate='%{lat:.4f}, %{lon:.4f}<br>Actual: %{marker.color:.2f}<extra></extra>'
    ))

    # Predicted sound speed trace (same dataframe)
    fig.add_trace(go.Scattergeo(
        lat=df_act['LATITUDE'],
        lon=df_act['LONGITUDE'],
        mode='markers',
        name='DNN Sound Speed',
        marker=dict(
            size=3,
            symbol='x',
            color=df_act['DNN'],
            colorscale='Hot',
            colorbar=dict(title='(m/s)'),
            cmin=df_act['DNN'].min(),
            cmax=df_act['DNN'].max(),
            opacity=0.9
        ),
        hovertemplate='%{lat:.4f}, %{lon:.4f}<br>Predicted: %{marker.color:.2f}<extra></extra>'
    ))

    fig.add_trace(go.Scattergeo(
        lat=df_act['LATITUDE'],
        lon=df_act['LONGITUDE'],
        mode='markers',
        name='KNN Sound Speed',
        marker=dict(
            size=6,
            color=df_act['KNN'],
            colorscale='jet',
            colorbar=dict(title='(m/s)'),
            cmin=df_act['KNN'].min(),
            cmax=df_act['KNN'].max(),
            opacity=0.5
        ),
        hovertemplate='%{lat:.4f}, %{lon:.4f}<br>Actual: %{marker.color:.2f}<extra></extra>'
    ))

    fig.update_layout(
        title_text='Actual vs Predicted Sound Speed (geographic)',
        legend=dict(x=0.02, y=0.98),
        geo=dict(projection_type='natural earth', showcoastlines=True, coastlinecolor='Black', showland=True, landcolor='LightGreen'),
        height=700,
        margin=dict(l=0, r=0, t=40, b=0)
    )

    # Write HTML output
    fig.write_html(out_html)
    print(f"Saved combined geoplot to: {out_html}")

    if open_in_browser:
        webbrowser.open(str(Path(out_html).resolve()))


if __name__ == '__main__':
    # Default path — update if your CSV name/path differs
    CSV_PATH = Path('d:/DS & ML/MLE/SoundSpeedEst/Predicted_Speed.csv')
    OUT = Path('geoplot_actual_vs_pred.html')
    try:
        plot_actual_vs_predicted_single(CSV_PATH, OUT, sample=10000, open_in_browser=True)
    except Exception as e:
        print('Error creating geoplot:', e)
