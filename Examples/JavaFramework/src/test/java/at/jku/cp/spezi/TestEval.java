package at.jku.cp.spezi;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import junit.framework.Test;
import junit.framework.TestCase;
import junit.framework.TestSuite;

public class TestEval extends TestCase
{
    /**
     * Create the test case
     *
     * @param testName name of the test case
     */
    public TestEval( String testName )
    {
        super( testName );
    }

    /**
     * @return the suite of tests being tested
     */
    public static Test suite()
    {
        return new TestSuite( TestEval.class );
    }
    
    public void testRoundtripLines() throws IOException
    {
    	File temp = File.createTempFile("testRoundtripLines_", ".txt");
        temp.deleteOnExit();
        
        List<String> expected = new ArrayList<>();
        expected.add("2389746293746076p91827383 20398 ritsn");
        expected.add("2398   9238     esnthrnsth *$^%^&(*&%^&*$%^ ");
        expected.add("a");
        
        Utils.writeToFile(temp.getAbsolutePath(), expected);
        
        List<String> actual = Files.readAllLines(Paths.get(temp.getAbsolutePath()));
        assertEquals(expected, actual);
    }

    public void testRoundtripDict() throws IOException
    {
    	File temp = File.createTempFile("testRoundtripDict_", ".dict");
        temp.deleteOnExit();
        
        Map<String, Integer> expected = new HashMap<>();
        expected.put("x", 0);
        expected.put("!@#$%^", 1);
        expected.put("002182$%^&*()(*&^%^&*()", 2);
     
        Utils.dictToFile(temp.getAbsolutePath(), expected);
        
        Map<String, Integer> actual = Utils.dictFromFile(temp.getAbsolutePath());
        assertEquals(expected, actual);
    }
    
    public void testTempoFileInput() throws IOException
    {
    	File temp = File.createTempFile("testFileInput_", ".dict");
        temp.deleteOnExit();
        
        List<String> lines = Arrays.asList("34.0	68.0	0.1");
        Utils.writeToFile(temp.getAbsolutePath(), lines);
        
        List<Double> actual = Utils.listFromFile(temp.getAbsolutePath());
        assertEquals(3, actual.size());
        assertEquals(Arrays.asList(34d, 68d, 0.1d), actual);
    }
    
    public void testTempoFileInputViaEvaluateEventFilesCorrect() throws IOException
    {
    	File gtFile = File.createTempFile("testFileInput_gt_", ".dict");
        gtFile.deleteOnExit();
        
    	File prFile = File.createTempFile("testFileInput_pr_", ".dict");
        prFile.deleteOnExit();
        
        File evFile = File.createTempFile("testFileInput_ev_", ".dict");
        evFile.deleteOnExit();

        List<String> gtLines = Arrays.asList("50.0	100.0	0.1");
        Utils.writeToFile(gtFile.getAbsolutePath(), gtLines);

        List<String> prLines = Arrays.asList("101.0");
        Utils.writeToFile(prFile.getAbsolutePath(), prLines);

        Runner.evaluateEventFiles(Runner.TEMPO, gtFile.getAbsolutePath(), prFile.getAbsolutePath(), evFile.getAbsolutePath(), 4d);
        Map<String, Integer> summary = Utils.dictFromFile(evFile.getAbsolutePath());
        System.out.println(summary);
    	assertEquals((int) 1, (int) summary.getOrDefault("correct", 0));
    	assertEquals((int) 0, (int) summary.getOrDefault("octcorrect", 0));
    	assertEquals((int) (1 * 1e6), (int) summary.getOrDefault("errorcorrect", 0));
    	assertEquals((int) 0, (int) summary.getOrDefault("errorwrong", 0));
    	assertEquals((int) 0, (int) summary.getOrDefault("wrong", 0));
    }
    
    public void testTempoFileInputViaEvaluateEventFilesOctaveCorrect() throws IOException
    {
    	File gtFile = File.createTempFile("testFileInput_gt_", ".dict");
        gtFile.deleteOnExit();
        
    	File prFile = File.createTempFile("testFileInput_pr_", ".dict");
        prFile.deleteOnExit();
        
        File evFile = File.createTempFile("testFileInput_ev_", ".dict");
        evFile.deleteOnExit();

        List<String> gtLines = Arrays.asList("50.0	100.0	0.1");
        Utils.writeToFile(gtFile.getAbsolutePath(), gtLines);

        List<String> prLines = Arrays.asList("51.0");
        Utils.writeToFile(prFile.getAbsolutePath(), prLines);

        Runner.evaluateEventFiles(Runner.TEMPO, gtFile.getAbsolutePath(), prFile.getAbsolutePath(), evFile.getAbsolutePath(), 4d);
        Map<String, Integer> summary = Utils.dictFromFile(evFile.getAbsolutePath());
        System.out.println(summary);
    	assertEquals((int) 0, (int) summary.getOrDefault("correct", 0));
    	assertEquals((int) 1, (int) summary.getOrDefault("octcorrect", 0));
    	assertEquals((int) (1 * 1e6), (int) summary.getOrDefault("errorcorrect", 0));
    	assertEquals((int) 0, (int) summary.getOrDefault("errorwrong", 0));
    	assertEquals((int) 0, (int) summary.getOrDefault("wrong", 0));
    }
    
    public void testTempoFileInputViaEvaluateEventFilesWrong() throws IOException
    {
    	File gtFile = File.createTempFile("testFileInput_gt_", ".dict");
        gtFile.deleteOnExit();
        
    	File prFile = File.createTempFile("testFileInput_pr_", ".dict");
        prFile.deleteOnExit();
        
        File evFile = File.createTempFile("testFileInput_ev_", ".dict");
        evFile.deleteOnExit();

        List<String> gtLines = Arrays.asList("50.0	100.0	0.1");
        Utils.writeToFile(gtFile.getAbsolutePath(), gtLines);

        List<String> prLines = Arrays.asList("20.0");
        Utils.writeToFile(prFile.getAbsolutePath(), prLines);

        Runner.evaluateEventFiles(Runner.TEMPO, gtFile.getAbsolutePath(), prFile.getAbsolutePath(), evFile.getAbsolutePath(), 4d);
        Map<String, Integer> summary = Utils.dictFromFile(evFile.getAbsolutePath());
        System.out.println(summary);
    	assertEquals((int) 0, (int) summary.getOrDefault("correct", 0));
    	assertEquals((int) 0, (int) summary.getOrDefault("octcorrect", 0));
    	assertEquals((int) 0, (int) summary.getOrDefault("errorcorrect", 0));
    	assertEquals((int) (80 * 1e6), (int) summary.getOrDefault("errorwrong", 0));
    	assertEquals((int) 1, (int) summary.getOrDefault("wrong", 0));
    }
    
    public void testEvalEvents() {
    	List<Double> gt = new ArrayList<>();
    	gt.add(0d);
    	gt.add(1d);
    	gt.add(2d);
    	
    	
    	List<Double> pr = new ArrayList<>();
    	pr.add(0.09d); // tp
    	pr.add(0.91d); // tp
    	pr.add(2.2d);  // fp
    	// and we missed the last entry from gt, so one fn as well!
    	
    	Map<String, Integer> summary = Utils.evaluateEventList(gt, pr, 0.1d);
    	System.out.println(summary);
    	assertEquals((int) 2, (int) summary.get("tp"));
    	assertEquals((int) 1, (int) summary.get("fp"));
    	assertEquals((int) 1, (int) summary.get("fn"));
    }
    
    public void testEvalEventsProduceCorrectCountsSimple() {
    	List<Double> gt = new ArrayList<>();
    	gt.add(0d);
    	gt.add(1d);
    	gt.add(2d);
    	
    	
    	List<Double> pr = new ArrayList<>();
    	pr.add(0.09d); // tp
    	pr.add(0.91d); // tp
    	pr.add(2.2d);  // fp
    	// and we missed the last entry from gt, so one fn as well!
    	
    	Map<String, Integer> summary = Utils.evaluateEventList(gt, pr, 0.1d);
    	System.out.println(summary);
    	assertEquals((int) 2, (int) summary.get("tp"));
    	assertEquals((int) 1, (int) summary.get("fp"));
    	assertEquals((int) 1, (int) summary.get("fn"));
    }

    public void testEvalEventsProduceCorrectCountsTooCrazy() {
    	List<Double> gt = new ArrayList<>();
    	gt.add(0d);
    	gt.add(1d);
    	gt.add(2d);
    	
    	List<Double> pr = new ArrayList<>();
    	pr.add(0.09d); // tp
    	pr.add(0.91d); // tp

    	// all of these will be fp's
    	for(int i=0; i < 1000; i++)
    	{
    		pr.add(i + 2.2d);
    	}
    	// and we missed the last entry from gt, so one fn as well!

    	Map<String, Integer> summary = Utils.evaluateEventList(gt, pr, 0.1d);
    	System.out.println(summary);
    	assertEquals((int) 2, (int) summary.get("tp"));
    	assertEquals((int) 1000, (int) summary.get("fp"));
    	assertEquals((int) 1, (int) summary.get("fn"));
    }
    
    public void testEvalTempoCorrect()
    {
    	List<Double> gt = new ArrayList<>();
    	gt.add(50d);
    	gt.add(100d);
    	gt.add(0.1d); // majority vote is 100
    	
    	List<Double> pr = new ArrayList<>();
    	pr.add(102d); // correct tempo@4%, error == 2
    	
    	Map<String, Integer> summary = Utils.evaluateTempo(gt, pr, 4d);
    	System.out.println(summary);
    	assertEquals((int) 1, (int) summary.getOrDefault("correct", 0));
    	assertEquals((int) 0, (int) summary.getOrDefault("octcorrect", 0));
    	assertEquals((int) (2 * 1e6), (int) summary.getOrDefault("errorcorrect", 0));
    	assertEquals((int) 0, (int) summary.getOrDefault("errorwrong", 0));
    	assertEquals((int) 0, (int) summary.getOrDefault("wrong", 0));
    }

    public void testEvalTempoWrong()
    {
    	List<Double> gt = new ArrayList<>();
    	gt.add(50d);
    	gt.add(100d);
    	gt.add(0.1d); // majority vote is 100
    	
    	List<Double> pr = new ArrayList<>();
    	pr.add(105d); // wrong tempo@4%, error == 5
    	
    	Map<String, Integer> summary = Utils.evaluateTempo(gt, pr, 4d);
    	System.out.println(summary);
    	assertEquals((int) 0, (int) summary.getOrDefault("correct", 0));
    	assertEquals((int) 0, (int) summary.getOrDefault("octcorrect", 0));
    	assertEquals((int) 0, (int) summary.getOrDefault("errorcorrect", 0));
    	assertEquals((int) (5 * 1e6), (int) summary.getOrDefault("errorwrong", 0));
    	assertEquals((int) 1, (int) summary.getOrDefault("wrong", 0));
    }
    
    public void testEvalTempoOctave()
    {
    	List<Double> gt = new ArrayList<>();
    	gt.add(50d);
    	gt.add(100d);
    	gt.add(0.1d); // majority vote is 50
    	
    	List<Double> pr = new ArrayList<>();
    	pr.add(51d); // correct octave tempo@4%, error == 1
    	// add real tempo here; should be ignored
    	for(int i = 0; i < 100; i++)
    	{
    		pr.add(100d + i);
    	}
    	
    	Map<String, Integer> summary = Utils.evaluateTempo(gt, pr, 4d);
    	System.out.println(summary);
    	assertEquals((int) 0, (int) summary.getOrDefault("correct", 0));
    	assertEquals((int) 1, (int) summary.getOrDefault("octcorrect", 0));
    	assertEquals((int) (1 * 1e6), (int) summary.getOrDefault("errorcorrect", 0));
    	assertEquals((int) 0, (int) summary.getOrDefault("errorwrong", 0));
    	assertEquals((int) 0, (int) summary.getOrDefault("wrong", 0));
    }

    public void testEvalTempoTooManyPredictions()
    {
    	List<Double> gt = new ArrayList<>();
    	gt.add(50d);
    	gt.add(100d);
    	gt.add(0.1d); // majority vote is 50
    	
    	List<Double> pr = new ArrayList<>();
    	pr.add(51d); // correct tempo@4%, error == 1
    	
    	Map<String, Integer> summary = Utils.evaluateTempo(gt, pr, 4d);
    	System.out.println(summary);
    	assertEquals((int) 0, (int) summary.getOrDefault("correct", 0));
    	assertEquals((int) 1, (int) summary.getOrDefault("octcorrect", 0));
    	assertEquals((int) (1 * 1e6), (int) summary.getOrDefault("errorcorrect", 0));
    	assertEquals((int) 0, (int) summary.getOrDefault("errorwrong", 0));
    	assertEquals((int) 0, (int) summary.getOrDefault("wrong", 0));
    }
    
    public void testEventListCleaningComputesMeanOfTooCloseEvents() {
    	List<Double> unclean = new ArrayList<>();
    	unclean.add(0d);
    	unclean.add(1d);
    	unclean.add(1.5d);
    	unclean.add(2d);
    	
    	
    	List<Double> expected_clean = new ArrayList<>();
    	expected_clean.add(0d);
    	expected_clean.add(1.25d);
    	expected_clean.add(2d);
    	
    	List<Double> actual_clean = Utils.cleanEventList(unclean, 0.6d);
    	assertEquals(expected_clean, actual_clean);
    }
    
    public void testEventListCleaningForEmptyEventList() {
    	List<Double> unclean = new ArrayList<>();
    	List<Double> expected_clean = new ArrayList<>();
    	
    	List<Double> actual_clean = Utils.cleanEventList(unclean, 0.6d);
    	assertEquals(expected_clean, actual_clean);
    }
}
