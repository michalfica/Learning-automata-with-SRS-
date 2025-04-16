package de.learnlib.example;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.Scanner;

import de.learnlib.acex.AcexAnalyzers;
import de.learnlib.algorithm.ttt.dfa.TTTLearnerDFA;
import de.learnlib.filter.cache.dfa.DFACacheOracle;
import de.learnlib.filter.cache.dfa.DFACaches;
import de.learnlib.filter.statistic.oracle.DFACounterOracle;
import de.learnlib.oracle.EquivalenceOracle.DFAEquivalenceOracle;
import de.learnlib.oracle.MembershipOracle.DFAMembershipOracle;
import de.learnlib.oracle.equivalence.DFASimulatorEQOracle;
import de.learnlib.oracle.membership.DFASimulatorOracle;
import de.learnlib.util.Experiment.DFAExperiment;
import de.learnlib.util.statistic.SimpleProfiler;
import net.automatalib.alphabet.Alphabet;
import net.automatalib.alphabet.impl.Alphabets;
import net.automatalib.alphabet.impl.GrowingMapAlphabet;
import net.automatalib.automaton.fsa.DFA;
import net.automatalib.automaton.fsa.impl.CompactDFA;
import net.automatalib.util.automaton.builder.AutomatonBuilders;
import net.automatalib.util.automaton.equivalence.DeterministicEquivalenceTest;

public class TTTExample1 {
    private static final String DFA_DESCRIPTION_FILE = "../../learnlib/examples/src/main/java/de/learnlib/example/DfaEx.txt"; 

    private static final char[] engAlphabet = "abcdefghijklmnopqrstuvwxyz".toCharArray();

    private TTTExample1(){
    }


    public static void main(String[] args) throws IOException{
        // load DFA and alphabet
        CompactDFA<Character> target = constructSUL();

        // DFALearningExample<Integer> target = DFABenchmarks.loadPeterson2();

        Alphabet<Character> sigma = target.getInputAlphabet();

        // construct a simulator membership query oracle
        DFAMembershipOracle<Character> sul = new DFASimulatorOracle<>(target);
        // oracle for counting queries wraps SUL
        DFACounterOracle<Character> mqOracle = new DFACounterOracle<>(sul);
        // create cache oracle
        DFACacheOracle<Character> cacheOracle = DFACaches.createCache(new GrowingMapAlphabet<>(sigma), mqOracle);

        // create a learner
        TTTLearnerDFA<Character> learner = new TTTLearnerDFA<>(sigma, cacheOracle, AcexAnalyzers.LINEAR_FWD);
        
        // create equivalence query oracle 
        DFAEquivalenceOracle<Character> eqOracle = new DFASimulatorEQOracle<>(target);
        

        // construct a learning experiment from
        // the learning algorithm and the conformance test.
        // The experiment will execute the main loop of
        // active learning
        DFAExperiment<Character> experiment = new DFAExperiment<>(learner, eqOracle, sigma);

        // turn on time profiling
        experiment.setProfile(true);

        // run experiment
        // long startTime = System.nanoTime();
        experiment.run();
        // long endTime = System.nanoTime();
        // long duration = (endTime - startTime);

        // get the result
        final DFA<?, Character> result = experiment.getFinalHypothesis();

        // assert we have the correct result
        assert DeterministicEquivalenceTest.findSeparatingWord(target, result, sigma) == null;
        
        // report results
        System.out.println("-------------------------------------------------------");
        // profiling
        SimpleProfiler.logResults();
        // learning statistics
        System.out.println(experiment.getRounds().getSummary());
        System.out.println(mqOracle.getStatisticalData().getSummary());

        // try (FileWriter expStatistic = new FileWriter(EXP_STATISTIC)) {
        //     expStatistic.write(experiment.getRounds().getSummary()+"\n");
        //     expStatistic.write(mqOracle.getStatisticalData().getSummary()+"\n");
        //     expStatistic.write("duration: " + (float)duration/1000000000 + "\n");
        // }
        System.out.println("-------------------------------------------------------");
    }

    /**
     * creates example from Angluin's seminal paper.
     *
     * @return example dfa
     */
    private static CompactDFA<Character> constructSUL() throws FileNotFoundException{
        File dfaDesc = new File(DFA_DESCRIPTION_FILE);
        CompactDFA<Character > dfa;
        try (Scanner dfaReader = new Scanner(dfaDesc)) {
            String data = dfaReader.nextLine();
            int n = Integer.parseInt(data.split(" ")[0]);
            int sigma_size = Integer.parseInt(data.split(" ")[1]);

            Alphabet<Character> sigma = Alphabets.characters(engAlphabet[0],engAlphabet[sigma_size-1]);
            dfa = AutomatonBuilders.newDFA(sigma).withInitial("q0").create();
            for( int i=1; i<n; i++){
                dfa.addState();
            }   
            for( int i=0; i<n; i++){
                data = dfaReader.nextLine();
                String[] transitions = data.split(" ");
                for( int j=0; j<sigma_size; j++ ){
                    dfa.addTransition(i, engAlphabet[j], Integer.parseInt(transitions[j]));
                }
            }   data = dfaReader.nextLine();
            String[] acceptingStates = data.split(" ");
            for(String state:   acceptingStates){
                dfa.setAccepting(Integer.parseInt(state), true);
            }
        }
        return dfa; 
    }
 
}
