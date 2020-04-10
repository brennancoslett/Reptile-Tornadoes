package at.jku.cp.spezi;

import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.logging.Level;
import java.util.logging.Logger;

public class Utils {

	public static void writeDataToFile(String filename, List<Double> data) {
		try {
			FileWriter outputwriter = new FileWriter(filename);
			for (Double d : data) {
				outputwriter.write(d + "\n");
			}
			outputwriter.flush();
			outputwriter.close();
		} catch (IOException ex) {
			Logger.getLogger(Runner.class.getName()).log(Level.SEVERE, null, ex);
		}
	}

	public static List<Double> listFromFile(String filename) {
		try {
			List<String> lines = Files.readAllLines(Paths.get(filename));
			List<Double> numbers = new ArrayList<>();
			for (String line : lines) {
				String[] tokens = line.trim().split("\\s+");
				if (tokens.length > 2) {
					// this is a tempo annotation, and we choose the tempo that
					// the majority of people predicted
					for(int t = 0; t < 3; t++)
					{
						numbers.add(Double.valueOf(tokens[t]));
					}
				} else {
					// for onsets and beats, we always take the first token as
					// the time
					numbers.add(Double.valueOf(tokens[0]));
				}
			}
			return numbers;
		} catch (Exception e) {
			// throw new RuntimeException(e);
			// can't be helped ...
			return new ArrayList<>();
		}
	}

	public static Map<String, Integer> dictFromFile(String filename) {
		try {
			List<String> lines = Files.readAllLines(Paths.get(filename));
			Map<String, Integer> dict = new HashMap<>();
			for (String line : lines) {
				String[] tokens = line.trim().split("\\s+");
				if (tokens.length == 2) {
					dict.put(tokens[0], Integer.valueOf(tokens[1]));
				} else {
					throw new RuntimeException("bogus dict file! '" + filename + "'");
				}
			}
			return dict;
		} catch (Exception e) {
			throw new RuntimeException(e);
		}
	}

	public static void dictToFile(String filename, Map<String, Integer> dict) {
		List<String> lines = new ArrayList<>();

		for (Map.Entry<String, Integer> entry : dict.entrySet()) {
			String key = entry.getKey().toString();
			String value = entry.getValue().toString();
			if (!key.equals(key.trim()))
				throw new RuntimeException("terrible idea to have whitespace surrounding keys");

			lines.add(key + " " + value);
		}

		writeToFile(filename, lines);
	}

	public static void writeToFile(String filename, List<String> lines) {
		try {
			Files.write(Paths.get(filename), lines);
		} catch (Exception e) {
			throw new RuntimeException(e);
		}
	}

	public static List<Double> filterNaNandInf(List<Double> events) {
		List<Double> filtered = new ArrayList<>();
		for (double u : events) {
			if (Double.isNaN(u) || Double.isInfinite(u)) {
				// let's treat weird numbers as if they were never being output
				System.out.println("NaN or Inf encountered in 'cleanEventList'");
			} else {
				filtered.add(u);
			}
		}
		return filtered;
	}

	/**
	 * this removes events from an event list that are closer together than the
	 * specified tolerance
	 * 
	 * @param events
	 * @param tolerance
	 * @return the filtered list of events
	 */
	public static List<Double> cleanEventList(List<Double> events, double tolerance) {
		List<Double> filtered = new ArrayList<>();
		for (int i = 0; i < events.size(); i++) {
			if (filtered.size() == 0) {
				filtered.add(events.get(i));
			}

			double u = events.get(i);
			double f = filtered.get(filtered.size() - 1);

			if (u - f >= tolerance) {
				// events are farther apart than the tolerance, simply copy
				// the current event over
				filtered.add(u);
			} else {
				// replace events closer together than the tolerance by
				// their mean
				filtered.remove(filtered.size() - 1);
				double mean = (u + f) / 2;
				filtered.add(mean);
			}
		}
		return filtered;
	}
	
	public static Map<String, Integer> evaluateTempo(List<Double> groundtruth, List<Double> prediction, double tolerance)
	{
		double gtTempo = 0d;
		double ocTempo = 0d;
		double fraction = 1d;
		double prTempo = 0d;

		if (groundtruth.size() == 1) {
			gtTempo = groundtruth.get(0);
			ocTempo = groundtruth.get(0);
			// tolerance = (gtTempo / 100d) * tolerance;
		} else if (groundtruth.size() == 3) {
			fraction = groundtruth.get(2);
			if(fraction > 0.5d) {
				gtTempo = groundtruth.get(0);
				ocTempo = groundtruth.get(1);
			} else {
				gtTempo = groundtruth.get(1);
				ocTempo = groundtruth.get(0);
			}
			// tolerance = (gtTempo / 100d) * tolerance;
		} else {
			throw new RuntimeException("weird tempo groundtruth!");
		}

		// no (or silly) predictions
		if (prediction.size() == 0) {
			Map<String, Integer> summary = new HashMap<>();
			summary.put("correct", 0);
			summary.put("octcorrect", 0);
			summary.put("wrong", 1);
			summary.put("errorcorrect", 0);
			summary.put("errorwrong", (int) (gtTempo * 1e6d)); // this is not in [us], but in [bpm] * 10^-6 ...
			return summary;
		}
		
		// in all other cases, the processor gave one or many predictions, so we consider only the first ...
		if (prediction.size() >= 1) {
			prTempo = prediction.get(0);
		}

		// did we hit the human majority tempo ?
		double deviation = (gtTempo / 100d) * tolerance;
		double lowerBound = gtTempo - deviation;
		double upperBound = gtTempo + deviation;
		
		if(lowerBound <= prTempo && prTempo <= upperBound) {
			Map<String, Integer> summary = new HashMap<>();
			summary.put("correct", 1);
			summary.put("octcorrect", 0);
			summary.put("wrong", 0);
			summary.put("errorcorrect", (int)(Math.abs(gtTempo - prTempo) * 1e6d)); // this is not in [us], but in [bpm] * 10^-6 ...
			summary.put("errorwrong", 0);
			return summary;
		}

		// if not, did we hit the human minority tempo ?
		lowerBound = ocTempo - deviation;
		upperBound = ocTempo + deviation;
		if(lowerBound <= prTempo && prTempo <= upperBound) {
			Map<String, Integer> summary = new HashMap<>();
			summary.put("correct", 0);
			summary.put("octcorrect", 1);
			summary.put("wrong", 0);
			summary.put("errorcorrect", (int)(Math.abs(ocTempo - prTempo) * 1e6d)); // this is not in [us], but in [bpm] * 10^-6 ...
			summary.put("errorwrong", 0);
			return summary;
		}
		
		// we did not hit either, so this is counted as wrong tempo
		Map<String, Integer> summary = new HashMap<>();
		summary.put("correct", 0);
		summary.put("octcorrect", 0);
		summary.put("wrong", 1);
		summary.put("errorcorrect", 0);
		summary.put("errorwrong", (int)(Math.abs(gtTempo - prTempo) * 1e6d)); // this is not in [us], but in [bpm] * 10^-6 ...;
		return summary;
	}

	public static Map<String, Integer> evaluateEventList(List<Double> groundtruth, List<Double> prediction, double tolerance) {

		if (groundtruth.size() == 0 && prediction.size() == 0) {
			Map<String, Integer> summary = new HashMap<>();
			summary.put("tp", 0);
			summary.put("fp", 0);
			summary.put("fn", 0);
			summary.put("error", 0);
			return summary;
		}

		if (groundtruth.size() == 0) {
			Map<String, Integer> summary = new HashMap<>();
			summary.put("tp", 0);
			summary.put("fp", prediction.size());
			summary.put("fn", 0);
			summary.put("error", 0);
			return summary;
		}

		if (prediction.size() == 0) {
			Map<String, Integer> summary = new HashMap<>();
			summary.put("tp", 0);
			summary.put("fp", 0);
			summary.put("fn", groundtruth.size());
			summary.put("error", 0);
			return summary;
		}

		Collections.sort(groundtruth);
		Collections.sort(prediction);

		int tp = 0;
		int fp = 0;
		int fn = 0;
		double cumulativeError = 0d;

		int trueCursor = 0;
		int predCursor = 0;
		while (trueCursor < groundtruth.size() && predCursor < prediction.size()) {
			double trueEvent = groundtruth.get(trueCursor);
			double predEvent = prediction.get(predCursor);

			double error = Math.abs(trueEvent - predEvent);

			if (error < tolerance) {
				// both events are close in time (within tolerance)
				// this is a true positive, we advance both cursors
				tp++;
				trueCursor++;
				predCursor++;
				cumulativeError += error;
			} else if (predEvent < trueEvent) {
				// the predicted event happens sooner than the current true
				// event
				// this is a false positive, we advance the prediction cursor
				// only
				fp++;
				predCursor++;
			} else if (predEvent > trueEvent) {
				// the predicted event happens later than the current true event
				// this is a false negative, we advance the true cursor only
				fn++;
				trueCursor++;
			} else {
				throw new RuntimeException(
						String.format("cannot match gtValue '%f' with prValue '%f'", trueEvent, predEvent));
			}
		}

		// what remains of the true events are the ones not predicted
		fn = fn + (groundtruth.size() - trueCursor);

		// what remains of the predicted are the ones falsely predicted
		fp = fp + (prediction.size() - predCursor);

		Map<String, Integer> summary = new HashMap<>();
		summary.put("tp", tp);
		summary.put("fp", fp);
		summary.put("fn", fn);
		summary.put("error", (int) (cumulativeError * 1e6d)); // in [us]
		return summary;
	}

	/*
	 * this is *terribly* inefficient ... but does not matter in the end
	 */
	public static double findNearest(List<Double> values, double target) {
		double minimum = Double.MAX_VALUE;
		double nearest = 0;

		for (double value : values) {
			double distance = Math.abs(target - value);
			if (distance < minimum) {
				minimum = distance;
				nearest = value;
			}
		}
		return nearest;

	}
}
