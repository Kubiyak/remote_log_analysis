<H1> Remote Log Analysis </H1>
<p>
Analyze remote log files on the localhost by copying the files in chunks onto the local host.
No local disk is used. Files are processed entirely in memory. Most log
file formats will include some timestamp. That timestamp can be used 
to efficiently restrict a search to a specified time range. </p>

<p>
The provided implementation focuses on reading logs from linux and 
docker-like environments. Other environments can be supported by
supplying a custom implementation of the RemoteExecutor layer which
fetches files and directory stat info.
</p>

<p>
A variety of log file formats can be supported by customizing 
the initialization parameters of or sub-classing the provided 
implementations. 
</p>