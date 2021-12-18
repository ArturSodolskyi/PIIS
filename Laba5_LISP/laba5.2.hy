(import math)

(setv *depth* 2)

(setv *player_x* 0)
(setv *player_y* 2)
(setv *enemy_x* 3)
(setv *enemy_y* 2)

(setv grid [
	[0 0 0 0 0]
	[0 1 0 1 0]
	[0 0 0 0 0]
	[0 0 1 0 0]
	[0 0 0 0 1]	
])

(defn get_nodes [node_x node_y]
	(setv nodes [])
	(if (> node_x 0)
		(do
			(setv left (get (get grid (- node_x 1)) node_y))			
			(if (= left 0)
				(nodes.append [(- node_x 1) node_y])
			)
		)
	)
	
	(if (< node_x 4)
		(do
			(setv right (get (get grid (+ node_x 1)) node_y))
			(if (= right 0)
				(nodes.append [(+ node_x 1) node_y])
			)
		)
	)
	
	(if (> node_y 0)
		(do
			(setv up (get (get grid node_x) (- node_y 1)))					
			(if (= up 0)
				(nodes.append [node_x (- node_y 1)])
			)
		)
	)
	
	(if (< node_y 4)
		(do
			(setv down (get (get grid node_x) (+ node_y 1)))
			(if (= down 0)
				(nodes.append [node_x (+ node_y 1)])
			)

		)
	)
	
	(return nodes)
)

(defn evaluate [node_x node_y enemy_x enemy_y]
	(setv x (- node_x enemy_x))
	(setv y (- node_y enemy_y))
	(return (math.sqrt (+ (* x x) (* y y))))
)

(defn minimax [is_max depth node_x node_y]
	(if (= depth *depth*)
		(do
			(return (evaluate node_x node_y *enemy_x* *enemy_y*))
		)
	)
	(if (= is_max True)
		(do
			(setv res [])
			(setv nodes (get_nodes node_x node_y))
			(for [node nodes]
				(setv next_x (get node 0))
				(setv next_y (get node 1))
				(setv minimax_res (minimax False depth next_x next_y))
				(res.append minimax_res)
			)
			(return (max res))
		)
		(do
			(setv res [])
			(setv nodes (get_nodes node_x node_y))
			(for [node nodes]
				(setv next_x (get node 0))
				(setv next_y (get node 1))
				(setv minimax_res (minimax True (+ depth 1) next_x next_y))
				(res.append minimax_res)
			)
			(return (min res))

		)
	)
)

(defn getIndexByValue [value collection]
	(setv i 0)
	(for [item collection]
		(if (= item value)
			(return i)
			(setv i (+ i 1))
		) 
	)
)

(defn optimalMovement [x y]
	(setv res [])
	(setv available_nodes (get_nodes x y))
	
	(for [node available_nodes]
		(setv next_x (get node 0))
		(setv next_y (get node 1))
		(setv minimax_res (minimax True 0 next_x next_y))
		(res.append minimax_res)
	)
	
	(setv index (getIndexByValue (max res) res))
	(print "Best movement: " (get available_nodes index))
)

(optimalMovement *player_x* *player_y*)