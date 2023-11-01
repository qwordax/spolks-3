# Subject

File transfer via UDP protocol. Handling exceptional situations.

# Description

Add to the client and the server the ability to transfer a file using the UDP
protocol. Pay attention to handling exceptional situations, such as physical
or software connection failure. This can be checked by enabling a firewall
with packet discarding without notification (`DROP` rule) and packet discarding
with notification (`REJECT` rule). Implement:

* mechanism for controlling the sequence of received datagrams.

* timeout mechanism — periodic sending of control packets to check the
  availability of the other side of the interaction, termination of the session
  with the client/server in case of absence of control packets within a fixed
  time interval.

* transmission flow control — reducing the load on the receiver in case of
  slow processing.
