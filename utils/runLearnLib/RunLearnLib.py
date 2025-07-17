import subprocess

"""
Class that is used to communicate with LearnLib repository.
Allows to:
    * compile LearLib repository,
    * run LearnLib implementation of L* or TTT algorithm,
    * returns the result of execution of the above algorithms and handles possible errors.
"""


class RunLearnLib:
    """
    TO DO:
        * czy dawać obsługiwać bardziej szczegółowo błędy?
        * Czy to odpowiednia ścieżka do uruchomienia?
    """

    COMPILATION_ERR = "[ERROR] COMPILATION ERROR :"

    def __init__(self, debug=False):
        self.debug = debug

    def __runCommand(self, command):
        proc = subprocess.run([command], shell=True, capture_output=True, text=True)
        assert proc.returncode == 0, (
            "Error during execution of subprocess.run "
            + command
            + "\nstout: "
            + proc.stdout
            + "\nstderr: "
            + proc.stderr
        )
        return proc

    def compileLearnLib(self):
        c = "cd ../../../learnlib/examples ; mvn clean install"
        _ = self.__runCommand(c)

        # output = proc.stdout
        # if proc.returncode != 0:
        #     compErr = output.find(self.COMPILATION_ERR)
        #     if compErr != -1:
        #         assert False, "Compilation error during 'mvn clean install'"

    def __getNumberofEQ(self, s):
        for l in s.splitlines():
            if l.startswith("Learning rounds"):
                return int(l.split()[-1])

    def runLstar(self):
        c = 'cd ../../../learnlib/examples ; mvn exec:java -q -Dexec.mainClass="de.learnlib.example.LstarExample1"'
        proc = self.__runCommand(c)  # ; cd ../../magisterka/test_algorithm/Lstar

        mq = "?"
        eq = self.__getNumberofEQ(proc.stdout)
        return [mq, eq]

    def runLstarWithAdvice(self):
        c = 'cd ../../../learnlib/examples ; mvn exec:java -q -Dexec.mainClass="de.learnlib.example.LstarExample_conv_cl_withAS"'
        proc = self.__runCommand(c)  # ; cd ../../magisterka/test_algorithm/Lstar

        mq = "?"
        eq = self.__getNumberofEQ(proc.stdout)
        return [mq, eq]
