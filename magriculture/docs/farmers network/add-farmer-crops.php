<?php include_once('header.php'); ?>

	<div class="content">

		<div class="breadcrumb"><a href="/home.php">Home</a> &gt; <a href="/farmers.php">Farmers</a></div>
		
		<h2>Select Crops</h2>
		
		<form class="standard" action="">
			<label for="form-crops">Top Crops in District</label>
			<select multiple="multiple" size="2" id="form-crops">
				<option>Tomatoes</option>
				<option>Potatoes</option>
				<option>Onions</option>
			</select>
			<input type="submit" name="submit" class="submit" value="Add to Farmer &raquo;" />
			
			<a href="/add-farmer-crops-search.php">Search for other crops not in list</a>
			
		</form>
		
		<h2>Menu</h2>
		<?php include_once('menu.php'); ?>		
	</div> <!-- /.content -->

<?php include_once('footer.php'); ?>