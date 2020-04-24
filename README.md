# chess

<h2>Requirements:</h2>
  -python 3.7<br>
  -tkinter<br>
  -copy<br>
  -numpy<br>
  -keras 2.3.1<br>
  -tensorflow 2.2.0<br>
  
<h2>Getting Started:</h2>
Clone the repository with <code>git clone https://github.com/Jefry99/chess</code>.<br>
<br>
<pre>
git clone https://github.com/Jefry99/chess
</pre>

Start by running:

<pre>
python run.py
</pre>
<br>
<h2>To train the nns:</h2><br>

Self_play create the batch of game to tran the nns:<br>

<pre>
python run.py self
</pre>
<br>
And then run the optimizer to update the weights:<br>
<br>
<pre>
python run.py opt
</pre>
<br>
To evaluate which model is better between the current one and the last one of the next gen:<br>
<br>
<pre>
python run.py eval
</pre>
This comand start 50 game between the model and save the winner as best model.