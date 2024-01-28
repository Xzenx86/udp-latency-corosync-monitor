*udp-latency*
A tiny end-to-end latency testing tool implemented using UDP protocol in a single Python file 📈. 

Support both one-way and round-trip latency measurement:
• `udp_latency.py` measures one-way latency.
• `udp_rrt.py` measures round-trip latency. (both with same arguments)

*Client Usage*

`python3 udp_latency.py -c -f/m &lt;frequency / bandwidth&gt; -n &lt;packet size&gt; -t &lt;running time&gt; --ip &lt;remote ip&gt; --port &lt;remote port&gt; --verbose &lt;bool&gt; --sync &lt;bool&gt;`

*Server Usage*

`python3 udp_latency.py -s -b &lt;buffer size&gt; --ip &lt;remote ip&gt; --port &lt;local port&gt; --verbose &lt;bool&gt; --sync &lt;bool&gt; --save &lt;records saving path&gt;`

*Arguments*
TODO