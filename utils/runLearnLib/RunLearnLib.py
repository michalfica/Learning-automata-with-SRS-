"""
Class that is used to communicate with LearnLib repository.
Allows to:
    * compile LearLib repository,
    * run LearnLib implementation of L* or TTT algorithm,
    * returns the result of execution of the above algorithms and handles possible errors.
"""

import subprocess


class RunLearnLib:

    def __init__(self):
        pass

    """
    TO DO: 
        * przymyśleć, CO mozę sie wydarzyć jakie błędy mgą wytąpić podczas kompilacji?
        * jakie błędy obsłużyć?
        * Czy to dobra ścieżka do uruchomienia?
    """

    def compileLearnLib(self):
        _ = subprocess.run(
            [
                "cd ../../../learnlib/examples ; mvn clean install; cd ../../magisterka/test_algorithm/Lstar"
            ],
            shell=True,
            capture_output=True,
            text=True,
        )
