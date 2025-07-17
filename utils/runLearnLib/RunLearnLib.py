"""
Class that is used to communicate with LearnLib repository.
Allows to:
    * compile LearLib repository,
    * run LearnLib implementation of L* or TTT algorithm,
    * returns the result of execution of the above algorithms and handles possible errors.
"""

import subprocess


class RunLearnLib:

    COMPILATION_ERR = "[ERROR] COMPILATION ERROR :"

    def __init__(self, debug=False):
        self.debug = debug

    """
    TO DO: 
        * przymyśleć, CO mozę sie wydarzyć jakie błędy mgą wytąpić podczas kompilacji?
        * jakie błędy obsłużyć?
        * Czy to dobra ścieżka do uruchomienia?
    """

    def compileLearnLib(self):
        proc = subprocess.run(
            [
                "cd ../../../learnlib/examples ; mvn clean install; cd ../../magisterka/test_algorithm/Lstar"
            ],
            shell=True,
            capture_output=True,
            text=True,
        )

        assert proc.returncode == 0, (
            "Error during execution of subprocess.run"
            # + "\nstout: " + proc.stdout
            + "\nstderr: "
            + proc.stderr
        )

        proc_output = proc.stdout
        compErr = proc_output.find(self.COMPILATION_ERR)
        assert compErr == -1, "Compilation error during 'mvn clean install'"

        return True
