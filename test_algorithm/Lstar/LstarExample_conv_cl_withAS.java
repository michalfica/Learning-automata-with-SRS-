package de.learnlib.example;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedList;
import java.util.Queue;
import java.util.Scanner;

import de.learnlib.algorithm.lstar.dfa.ClassicLStarDFA;
import de.learnlib.algorithm.lstar.dfa.ClassicLStarDFABuilder;
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
import net.automatalib.word.Word;
import net.automatalib.word.WordBuilder;

public class LstarExample_conv_cl_withAS {
    private static final String DFA_DESCRIPTION_FILE = "../../learnlib/examples/src/main/java/de/learnlib/example/DfaEx.txt";

    private static final char[] engAlphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ".toCharArray();

    private LstarExample_conv_cl_withAS(){
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
    private static Word<Character> findDistinguishingWord(DFA<Integer, Character> dfa, Alphabet<Character> alphabet, Integer q1, Integer q2) {
        Queue<String> queue = new LinkedList<>();
        queue.clear();
        queue.add("");

        HashSet<String> visited = new HashSet<>();
        visited.clear();
        visited.add(q1.toString()+"#"+q2.toString());

        while (!queue.isEmpty()) {
            String w = queue.poll();
            Word<Character> word = convertStringToWord(w);

            if (dfa.computeStateOutput(q1,word).booleanValue() != dfa.computeStateOutput(q2, word).booleanValue()) {
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

    // For every state find an access sequence 
    private static HashMap<Integer, String> computeAccessSequences(DFA<Integer, Character> dfa, Alphabet<Character> alphabet) {
        Queue<Integer> queue = new LinkedList<>();
        queue.clear();

        HashMap<Integer, String> visited = new HashMap<>();
        visited.clear();

        Integer q0 = dfa.getInitialState();
        visited.put(q0, "");

        queue.add(q0);

        while(!queue.isEmpty()){

            Integer q = queue.poll();
            for(Character symbol : alphabet ){
                Integer next_q = dfa.getSuccessor(q, symbol);
                if( visited.get(next_q)== null){
                    visited.put(next_q, visited.get(q)+symbol);
                    queue.add(next_q);
                }
            }
        }
        return visited; // No distinguishing word found
    }

    public static DefaultQuery<Character, Boolean> checkConsistencywithSRS(input_data target, DFA<Integer, Character> hyp, Alphabet<Character> inputs)throws IOException{
        // System.out.println(hyp.getStates().getClass().getSimpleName());
        HashMap<Integer, String> access_sequences = computeAccessSequences(hyp, inputs);
        int inputs_size = inputs.size();
        for( int i=0; i<target.fst_cl; i++){
            for( int j=target.lst_cl+1; j<inputs_size; j++){  
                for( Integer q :  hyp.getStates()){
                    
                    // (inputs[i]inputs[j], inputs[j]inputs[i]) \in Advice System  
                    Integer q1 = hyp.getSuccessor(q, convertStringToWord(inputs.apply(i).toString() + inputs.apply(j).toString()));
                    Integer q2 = hyp.getSuccessor(q, convertStringToWord(inputs.apply(j).toString() + inputs.apply(i).toString()));
                    // System.out.print("przesjac z " + q + "po literce " + inputs.apply(i).toString() + inputs.apply(j).toString() + " to  q1 =  " + q1 + " a po literce " + inputs.apply(j).toString() + inputs.apply(i).toString() + " to q2 = " + q2 +"\n");
                    if( q1.intValue()!= q2.intValue() ){  // inconsistency with Advice System 
                        Word<Character> potentialCe1 = convertStringToWord(access_sequences.get(q)).append(inputs.apply(i)).append(inputs.apply(j));
                        Word<Character> potentialCe2 = convertStringToWord(access_sequences.get(q)).append(inputs.apply(j)).append(inputs.apply(i));
                        Word<Character> sep = findDistinguishingWord(hyp, inputs, q1, q2);
                        potentialCe1 = potentialCe1.concat(sep);
                        potentialCe2 = potentialCe2.concat(sep);

                        // System.out.print("potence1 : " + potentialCe1 + " potence2 : " + potentialCe2 +'\n');
                        Boolean status = target.dfa.computeOutput(potentialCe1);
                        // System.out.print(status + "\n");
                        // System.out.print(hyp.computeOutput(potentialCe1) + "\n");

                        if( status.booleanValue()!=hyp.computeOutput(potentialCe1).booleanValue()){
                            return new DefaultQuery<>(potentialCe1, status);
                        }
                        else{
                            return new DefaultQuery<>(potentialCe2, target.dfa.computeOutput(potentialCe2));
                        }
                    }
                }
            }
        }
        return null;
    }

    public static DFA<?, Character> runExperiment(input_data target, ClassicLStarDFA<Character> learningAlgorithm, DFAEquivalenceOracle<Character> equivalenceAlgorithm, Alphabet<Character> inputs) throws IOException{
        Counter rounds = new Counter("Learning rounds", "#");
        System.out.println("RUN EXPERIMENT");
        rounds.increment();
        learningAlgorithm.startLearning();
        
        while (true) {
            System.out.print("Starting round: ");
            System.out.print(rounds.getCount());
            System.out.print("\n");

            DFA<Integer, Character> hyp = (DFA<Integer, Character>) learningAlgorithm.getHypothesisModel();

            DefaultQuery<Character, Boolean> ceFromConsistencyCheck = checkConsistencywithSRS(target, hyp, inputs);
            // System.out.println("ceFromConsistencyCheck = " + ceFromConsistencyCheck);
            // Visualization.visualize(hyp, inputs);
            while( ceFromConsistencyCheck!=null ){
                final boolean refined = learningAlgorithm.refineHypothesis(ceFromConsistencyCheck);
                assert refined;
                hyp = (DFA<Integer, Character>)  learningAlgorithm.getHypothesisModel();
                ceFromConsistencyCheck = checkConsistencywithSRS(target, hyp, inputs);
                // System.out.println("ceFromConsistencyCheck = " + ceFromConsistencyCheck);
                // Visualization.visualize(hyp, inputs);
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

        // return null; 
    }

    public static class input_data{
        public CompactDFA<Character> dfa;
        public int fst_cl;
        public int lst_cl;

        public input_data(){

        }
        public input_data(CompactDFA<Character> _dfa, int _fst_cl, int _lst_cl) {
            dfa = _dfa;
            fst_cl = _fst_cl;
            lst_cl = _lst_cl;
        }
        
    }
    public static void main(String[] args) throws IOException{
        
        // load DFA and alphabet
        input_data target = constructSUL();
        // CompactDFA<Character> target = constructSUL();
        Alphabet<Character> sigma = target.dfa.getInputAlphabet();

        // HashMap<Integer,String> accsseq = computeAccessSequences(target.dfa, sigma);
        // System.out.print(accsseq);

        // Visualization.visualize(target, sigma);

        // construct a simulator membership query oracle
        DFAMembershipOracle<Character> sul = new DFASimulatorOracle<>(target.dfa);
        // oracle for counting queries wraps sul
        DFACounterOracle<Character> mqOracle = new DFACounterOracle<>(sul);
        // create cache oracle
        DFACacheOracle<Character> cacheOracle = DFACaches.createCache(new GrowingMapAlphabet<>(sigma), mqOracle);
        // create a learner
        ClassicLStarDFA<Character> learner = 
                new ClassicLStarDFABuilder<Character>().withAlphabet(sigma)
                                                       .withOracle(cacheOracle)
                                                       .create();
        
        // create equivalence query oracle 
        DFAEquivalenceOracle<Character> eqOracle = new DFASimulatorEQOracle<>(target.dfa);
        
        // run experiment and get the result
        final DFA<?, Character> result = runExperiment(target, learner, eqOracle, sigma);
        System.out.println(mqOracle.getStatisticalData().getSummary());
    }


    private static input_data constructSUL() throws FileNotFoundException{
        File dfaDesc = new File(DFA_DESCRIPTION_FILE);
        CompactDFA<Character > dfa;
        input_data result = new input_data();
        try (Scanner dfaReader = new Scanner(dfaDesc)) {
            String data = dfaReader.nextLine();
            int n = Integer.parseInt(data.split(" ")[0]);
            int sigma_size = Integer.parseInt(data.split(" ")[1]);
            int fst_cl = Integer.parseInt(data.split(" ")[2]);
            int lst_cl = Integer.parseInt(data.split(" ")[3]);

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

            result.dfa=dfa;
            result.fst_cl =  fst_cl;
            result.lst_cl = lst_cl;
        }
        return result; 
    }
 
}