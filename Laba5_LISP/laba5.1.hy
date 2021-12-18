(import [pandas :as pd])
(import [numpy :as np])

(setv path "statistics.csv")
(setv data (pd.read_csv path))

(setv time (get data "time"))
(print "math expectation of time:"  (/ (np.sum time) (len time)))

(setv score (get data "score"))
(setv sample_mean (/ (np.sum score) (len score)))
(setv sum_of_squares (np.sum (* score score)))
(setv dispersion_of_score (- (/ sum_of_squares (len score)) (* sample_mean sample_mean)))
(print "Dispersion of score:" dispersion_of_score)