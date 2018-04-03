PyWorks - a small concurrent framework for Python

  Ever since i first worked with threads in Java 15 years ago, I have been
struggeling with the concept. Before that I was used to C and a homegrown "OS"
called Daros. It had Task "preemtive processes", Messages and Queues. For me
it was much easier to comprehend the one Task == one thread concept.
No synchronized keyword, only place you had to take a little care was if you
used shared memory (which was rare)

  In 2004 we therefore inplemented Coworks in Java, a concurrent object model
for Java. Also known as the Task pattern. Since then we have implemented many
larger projects all over the world. The concept is easy for developers to
understand and generally performs very well.

  The other evening I decided to try to implement my version of Coworks in
Python. Inspired by Donovan Preston's (@donovanpreston) talk at Pycon 2010
about his implementation of Task's in Python I decided to try my self.

  Pyworks implements two types of concurrent classes: Actor and Task. Actor
is a simple concurrent class and Task is a specialized form of Actor. Actor
has a few simple methods: actor, timeout, notify and observe. Task is more
complex supporting State pattern and methods for controlled startup sequence,
configuration etc.

  It is a simple as it gets. Subclasses of Task run in their own thread.
Task's can access each other by calling self.actor("SomeActor") to get
a Proxy for that Task. You can call all methods on the other Task. The Method
is sent on a Queue and executed in the other Task's thread.

  If you need a return value you can use the Future patten.

  Every Task can listen on other Task's via the self.observe("SomeActor")
method. A listener must implement all Output methods of the Task being
listened on.

  Every Task has a State (default is it self), which handle all incoming
Methods. This means that States in Task are very easy to implement.

  No thought or time whatsoever has been put into performance, this is a study
only.

run test test program by simply doing:
$ python pywork.py --run

Works on python3

Rene Nejsum
rene@pylots.com

Copyright (C) 2012-

