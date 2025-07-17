import subprocess

"""
Class that is used to communicate with LearnLib repository.
Allows to:
    * compile LearLib repository,
    * run LearnLib implementation of L* or TTT algorithm,
    * returns the result of execution of the above algorithms and handles possible errors.
"""


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

    # WĄTPLIWOŚĆI:
    #  * czy komenda jest poprawna, czy powinienem zmieniać ścieżkę?

    # TO DO:
    # * uruchomienie liku z Learnliba i zwrócenie wyniku
    def compileLearnLib(self):
        proc = subprocess.run(
            ["cd ../../../learnlib/examples ; mvn clean install"],
            shell=True,
            capture_output=True,
            text=True,
        )

        proc_output = proc.stdout
        if proc.returncode != 0:
            compErr = proc_output.find(self.COMPILATION_ERR)
            if compErr != -1:
                assert False, "Compilation error during 'mvn clean install'"
            else:
                assert False, (
                    "Error during execution of subprocess.run"
                    + "\nstout: "
                    + proc.stdout
                    + "\nstderr: "
                    + proc.stderr
                )
