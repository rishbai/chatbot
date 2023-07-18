import os
import pickle
import numpy as np
import plotly.graph_objects as go
from sklearn.decomposition import PCA
from matplotlib.cm import get_cmap

# Set the path to the pickles directory
pickle_path = os.getcwd() + "/pickles/"

# Load the embeddings and chunk list from the pickles
embeddings = pickle.load(open(pickle_path + 'embeddings.pickle', 'rb'))
chunk_list = pickle.load(open(pickle_path + 'chunks.pickle', 'rb'))

# Convert embeddings to a NumPy array
embeddings = np.array(embeddings)

# Perform PCA to reduce dimensionality to 3
pca = PCA(n_components=3)
embeddings_3d = pca.fit_transform(embeddings)

# Scale the embeddings to range from -0.5 to 0.5
scale_factor = 1.0 / np.max(np.abs(embeddings_3d))
embeddings_3d *= scale_factor

# Get the number of unique files
unique_files = list(set(chunk_list))
num_files = len(unique_files)

# Create a colormap
cmap = get_cmap('tab10')

# Create a 3D scatter plot
fig = go.Figure()

# Plot the embeddings in the reduced 3D space with different colors for each file
marker_size = 8  # Increase the marker size
marker_opacity = 0.5  # Adjust the marker opacity
for i, embedding in enumerate(embeddings_3d):
    x, y, z = embedding
    file_index = unique_files.index(chunk_list[i])
    color_index = (file_index + 1) % num_files  # Shift the color index to avoid blue
    color = cmap(color_index)
    fig.add_trace(
        go.Scatter3d(
            x=[x],
            y=[y],
            z=[z],
            mode='markers',
            marker=dict(color=color, size=marker_size, opacity=marker_opacity)
        )
    )

# Add more plot points (you can adjust the range and step size as needed)
additional_points = 100
extra_embeddings = np.random.uniform(low=-0.5, high=0.5, size=(additional_points, 3))
extra_color = 'rgba(153, 50, 204, 0.7)'  # Dark pink, almost purple color with opacity
for embedding in extra_embeddings:
    x, y, z = embedding
    fig.add_trace(
        go.Scatter3d(
            x=[x],
            y=[y],
            z=[z],
            mode='markers',
            marker=dict(color=extra_color, size=marker_size, opacity=marker_opacity)
        )
    )

# Set the axis labels
fig.update_layout(scene=dict(xaxis_title='x', yaxis_title='y', zaxis_title='z'))

fig.update_layout(title='3D Scatter Plot of Embeddings Similarity')

# Create a color legend
color_legend = []
for i, file_name in enumerate(unique_files):
    color_index = (i + 1) % num_files  # Shift the color index to avoid blue
    color = cmap(color_index)
    color_legend.append((color, file_name))

# Add the color legend to the plot
fig.update_layout(legend=dict(title='File Legend'))

# Show the plot
fig.show()
