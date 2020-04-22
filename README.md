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
cd board
</pre>

Start by running:

<pre>
python board.py
</pre>
<br>
For the developers argument <code>-d</code> start directly a game.<br>
<br>
<pre>
python board.py -d
</pre>
<br>
<h2>To train the nns:</h2><br>

Run self_play to create the batch of game to tran the nns:<br>

<pre>
python self_play.py
</pre>
<br>
And then run the optimizer to update the weights:<br>
<br>
<pre>
python optimize.py
</pre>