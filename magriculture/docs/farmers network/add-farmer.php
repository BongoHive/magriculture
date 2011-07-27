<?php include_once('header.php'); ?>

	<div class="content">

		<div class="breadcrumb"><a href="/home.php">Home</a> &gt; <a href="/farmers.php">Farmers</a></div>
		
		<h2>New Farmer</h2>
		
		<form class="standard" action="/add-farmer-crops.php">
			<label for="form-name">Name</label>
			<input type="text" id="form-name" />
			
			<label for="form-surname">Surname</label>
			<input type="text" id="form-surname" />
			
			<label for="form-mobile">Mobile Number</label>
			<input type="text" id="form-mobile" />

			<label for="form-region">Region</label>
			<select id="form-region">
				<option>Stellenbosch</option>
				<option>Paarl</option>
				<option>Cape Town</option>
			</select>
			
			<input type="submit" name="submit" class="submit" value="Save and add crops &raquo;" />
			
		</form>		
		
		<h2>Menu</h2>
		<?php include_once('menu.php'); ?>		
	</div> <!-- /.content -->

<?php include_once('footer.php'); ?>