package de.learnlib.example;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.HashSet;
import java.util.LinkedList;
import java.util.Queue;
import java.util.Scanner;

import de.learnlib.acex.AcexAnalyzers;
import de.learnlib.algorithm.ttt.dfa.TTTHypothesisDFA;
import de.learnlib.algorithm.ttt.dfa.TTTLearnerDFA;
import de.learnlib.algorithm.ttt.dfa.TTTStateDFA;
import de.learnlib.filter.cache.dfa.DFACacheOracle;
import de.learnlib.filter.cache.dfa.DFACaches;
import de.learnlib.filter.statistic.Counter;
import de.learnlib.filter.statistic.oracle.DFACounterOracle;
import de.learnlib.oracle.EquivalenceOracle.DFAEquivalenceOracle;
import de.learnlib.oracle.MembershipOracle.DFAMembershipOracle;
import de.learnlib.oracle.equivalence.DFASimulatorEQOracle;
import de.learnlib.oracle.membership.DFASimulatorOracle;
import de.learnlib.query.DefaultQuery;
import net.automatalib.alphabet.Alphabet;
import net.automatalib.alphabet.impl.Alphabets;
import net.automatalib.alphabet.impl.GrowingMapAlphabet;
import net.automatalib.automaton.fsa.DFA;
import net.automatalib.automaton.fsa.impl.CompactDFA;
import net.automatalib.util.automaton.builder.AutomatonBuilders;
import net.automatalib.util.automaton.equivalence.DeterministicEquivalenceTest;
import net.automatalib.word.Word;
import net.automatalib.word.WordBuilder;

public class TTTExample1_withAS {
    private static final String DFA_DESCRIPTION_FILE = "../../learnlib/examples/src/main/java/de/learnlib/example/DfaEx4.txt";

    private static final char[] engAlphabet = "abcdefghijklmnopqrstuvwxyz".toCharArray();

    private TTTExample1_withAS(){
    }

    private static Word<Character> convertStringToWord(String w){
        WordBuilder<Character> wb = new WordBuilder<>(null, 0);
        for( char c : w.toCharArray()){
            wb.append(c);
        }
        Word<Character> word = wb.toWord();
        return word;
    }

    // Find a distinguishing word for two DFA states
    private static Word<Character> findDistinguishingWord(TTTHypothesisDFA<Character> dfa, Alphabet<Character> alphabet, TTTStateDFA<Character> q1, TTTStateDFA<Character> q2) {
        Queue<String> queue = new LinkedList<>();
        queue.clear();
        queue.add("");

        HashSet<String> visited = new HashSet<>();
        visited.clear();
        visited.add(q1.toString()+"#"+q2.toString());

        while (!queue.isEmpty()) {
            String w = queue.poll();
            Word<Character> word = convertStringToWord(w);

            if (dfa.computeStateOutput(q1,word) != dfa.computeStateOutput(q2, word)) {
                return word; // Found a distinguishing word
            }

            for (Character symbol : alphabet) {
                String next_q1 = dfa.getSuccessor(q1, convertStringToWord(w+symbol)).toString();
                String next_q2 = dfa.getSuccessor(q2, convertStringToWord(w+symbol)).toString();

                if( !visited.contains(next_q1 + "#" + next_q2)){
                    queue.add(w + symbol);
                    visited.add(next_q1 + "#" + next_q2);
                }
            }
        }
        return null; // No distinguishing word found
    }

    public static DefaultQuery<Character, Boolean> checkConsistencywithSRS(CompactDFA<Character> target, TTTHypothesisDFA<Character> hyp, Alphabet<Character> inputs)throws IOException{
        int inputs_size = inputs.size();
        for( int i=0; i<inputs_size/2; i++){
            for( int j=inputs_size/2; j<inputs_size; j++){  
                for( TTTStateDFA<Character> q :  hyp.getStates()){
                    
                    // (inputs[i]inputs[j], inputs[j]inputs[i]) \in Advice System  
                    TTTStateDFA<Character> q1 = hyp.getSuccessor(q, convertStringToWord(inputs.apply(i).toString() + inputs.apply(j).toString()));
                    TTTStateDFA<Character> q2 = hyp.getSuccessor(q, convertStringToWord(inputs.apply(j).toString() + inputs.apply(i).toString()));
                    if( q1 != q2 ){  // inconsistency with Advice System 

                        Word<Character> potentialCe1 = q.getAccessSequence().append(inputs.apply(i)).append(inputs.apply(j));
                        Word<Character> potentialCe2 = q.getAccessSequence().append(inputs.apply(j)).append(inputs.apply(i));
                        
                        Word<Character> sep = findDistinguishingWord(hyp, inputs, q1, q2);
                        potentialCe1 = potentialCe1.concat(sep);
                        potentialCe2 = potentialCe2.concat(sep);

                        Boolean status = target.computeOutput(potentialCe1);
                        if( status!=hyp.computeOutput(potentialCe1)){
                            return new DefaultQuery<>(potentialCe1, status);
                        }
                        else{
                            return new DefaultQuery<>(potentialCe2, target.computeOutput(potentialCe2));
                        }
                    }
                }
            }
        }
        return null;
    }

    public static TTTHypothesisDFA<Character> runExperiment(CompactDFA<Character> target, TTTLearnerDFA<Character> learningAlgorithm, DFAEquivalenceOracle<Character> equivalenceAlgorithm, Alphabet<Character> inputs) throws IOException{
        Counter rounds = new Counter("Learning rounds", "#");

        rounds.increment();
        learningAlgorithm.startLearning();

        while (true) {
            System.out.print("Starting round: ");
            System.out.print(rounds.getCount());
            System.out.print("\n");

            TTTHypothesisDFA<Character> hyp = (TTTHypothesisDFA<Character>) learningAlgorithm.getHypothesisModel();

            DefaultQuery<Character, Boolean> ceFromConsistencyCheck = checkConsistencywithSRS(target, hyp, inputs);
            while( ceFromConsistencyCheck!=null ){
                final boolean refined = learningAlgorithm.refineHypothesis(ceFromConsistencyCheck);
                assert refined;
                hyp = (TTTHypothesisDFA<Character>) learningAlgorithm.getHypothesisModel();
                ceFromConsistencyCheck = checkConsistencywithSRS(target, hyp, inputs);
            }

            DefaultQuery<Character, Boolean> ce = equivalenceAlgorithm.findCounterExample(hyp, inputs);

            if (ce == null) {
                System.out.println("Learning rounds: " + rounds.getCount());
                return hyp;
            }

            // next round ...
            rounds.increment();
            final boolean refined = learningAlgorithm.refineHypothesis(ce);
            assert refined;
        }

    }

    public static void main(String[] args) throws IOException{
        
        // load DFA and alphabet
        CompactDFA<Character> target = constructSUL();
        Alphabet<Character> sigma = target.getInputAlphabet();

        // construct a simulator membership query oracle
        DFAMembershipOracle<Character> sul = new DFASimulatorOracle<>(target);
        // oracle for counting queries wraps sul
        DFACounterOracle<Character> mqOracle = new DFACounterOracle<>(sul);
        // create cache oracle
        DFACacheOracle<Character> cacheOracle = DFACaches.createCache(new GrowingMapAlphabet<>(sigma), mqOracle);

        // create a learner
        TTTLearnerDFA<Character> learner = new TTTLearnerDFA<>(sigma, cacheOracle, AcexAnalyzers.LINEAR_FWD);
        
        // create equivalence query oracle 
        DFAEquivalenceOracle<Character> eqOracle = new DFASimulatorEQOracle<>(target);
        
        // run experiment and get the result
        final DFA<?, Character> result = runExperiment(target, learner, eqOracle, sigma);
        // assert we have the correct result
        System.out.print(DeterministicEquivalenceTest.findSeparatingWord(target, result, sigma));

        System.out.println(mqOracle.getStatisticalData().getSummary());
    }


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