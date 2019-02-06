from errbot.backends.base import Message as ErrbotMessage
from errbot import botcmd
from errbot import BotPlugin
from errbot import Command
from errbot import ValidationException
import trio


class TrioExample(BotPlugin):

    @botcmd
    def trio_example(self, msg, args) -> None:
        """
        A quick example errbot plugin with trio

        """
        trio.run(self.parent, msg)
        return

    @botcmd
    def trio_tracer(self, msg, args) -> None:
        """
        A quick example errbot plugin with trio with some tracing!
        """
        trio.run(self.parent, msg, instruments=[Tracer()])
        return

    async def child1(self, msg):
        self.send(msg.to, text="  child1: started! sleeping now...")
        await trio.sleep(1)
        self.send(msg.to, text="  child1: exiting!")

    async def child2(self, msg):
        self.send(msg.to, text="  child2: started! sleeping now...")
        await trio.sleep(1)
        self.send(msg.to, text="  child2: exiting!")

    async def parent(self, msg):
        self.send(msg.to, text="parent: started!")
        async with trio.open_nursery() as nursery:
            self.send(msg.to, text="parent: spawning child1...")
            nursery.start_soon(self.child1, msg)

            self.send(msg.to, text="parent: spawning child2...")
            nursery.start_soon(self.child2, msg)

            self.send(msg.to, text="parent: waiting for children to finish...")
            # -- we exit the nursery block here --
        self.send(msg.to, text="parent: all done!")


class Tracer(trio.abc.Instrument):
    def before_run(self):
        print("!!! run started")

    def _print_with_task(self, msg, task):
        # repr(task) is perhaps more useful than task.name in general,
        # but in context of a tutorial the extra noise is unhelpful.
        print("{}: {}".format(msg, task.name))

    def task_spawned(self, task):
        self._print_with_task("### new task spawned", task)

    def task_scheduled(self, task):
        self._print_with_task("### task scheduled", task)

    def before_task_step(self, task):
        self._print_with_task(">>> about to run one step of task", task)

    def after_task_step(self, task):
        self._print_with_task("<<< task step finished", task)

    def task_exited(self, task):
        self._print_with_task("### task exited", task)

    def before_io_wait(self, timeout):
        if timeout:
            print("### waiting for I/O for up to {} seconds".format(timeout))
        else:
            print("### doing a quick check for I/O")
        self._sleep_time = trio.current_time()

    def after_io_wait(self, timeout):
        duration = trio.current_time() - self._sleep_time
        print("### finished I/O check (took {} seconds)".format(duration))

    def after_run(self):
        print("!!! run finished")