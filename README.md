<H1> Remote Log Analysis </H1>
<H2>Overview</H2>
<p>
A log file is a sequence of bytes where some immutability guarantee exists for
already written data. New data can be appended to the end of a log file but bytes
which have already been written should not change while accessed via this framework. 
Such logs can be large and efficiently processing such logs in chunks can 
save on data transfer costs and time. Note that any static file can be considered a 
log file.
</p>
<p>
The above definition is very general and opens the door to just about any file-like object
which can be accessed over the network. By this definition
a network stream itself can be considered a log file and a goal of this framework is to 
provide the groundwork to make such extensions possible. In general, The more structured 
the data, the more useful this framework is for skipping efficiently within
the log file but this framework can be useful for accessing just about any stream-like 
object over a network.
</p>
<p>
Examples will be developed over time to showcase the possibilities.
</p>
<H2>Tests</H2>
<p>To run the tests do the following from the project root directory:</p>
<pre>poetry install</pre>
<pre>pytest -s tests/</pre>
<p>To run the tests with coverage try this from the project root directory:</p>
<pre>pytest -s --cov=remote_log_analysis --cov-report=html tests/</pre>
