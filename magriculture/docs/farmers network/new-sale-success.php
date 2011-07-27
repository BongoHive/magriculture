<?php include_once('header.php'); ?>

	<div class="content">

		<div class="breadcrumb"><a href="/home.php">Home</a> &gt; <a href="/farmers.php">Farmers</a> &gt; John Richards</div>
		
		<div class="meta">
			<div class="success">New Sale Registered</div>
		
			<h2>John Richards <span>Stellenbosch</span></h2>
			<span class="subtitle">Grapes</span>
		</div> <!-- /.meta -->
		
		<ul class="menu">
			<li><a href="/new-sale.php"><img src="images/icon-calendar.gif" alt="icon-calendar" width="16" height="16" />Register new Sale &raquo;</a></li>
			<li><a href="/message-farmer.php"><img src="images/icon-message.gif" alt="icon-message" width="16" height="16" />Message Farmer &raquo;</a></li>
			<li><a href="/add-note.php"><img src="images/icon-write.gif" alt="icon-write" width="16" height="16" />Add Note &raquo;</a></li>
			<li><a href="/farmer-profile.php"><img src="images/icon-profile.gif" alt="Farmers" width="16" height="16" />View Profile &raquo;</a></li>
		</ul>

		<div class="tabs">Sales | <a href="/farmer-detail-messages.php">Messages</a> | <a href="/farmer-detail-notes.php">Notes</a></div>

		<ul class="list">
			<li>
				<span class="text"><a href="/sale-detail.php">55 Tomato Boxes</a></span><br/>
				<span class="subtitle">25 AUG 2011, 10:45PM</span>
			</li>
			<li>
				<span class="text"><a href="/sale-detail.php">3000 Onion packets</a></span><br/>
				<span class="subtitle">25 AUG 2011, 10:45PM</span>
			</li>
			<li>
				<span class="text"><a href="/sale-detail.php">44000 Potatoes</a></span><br/>
				<span class="subtitle">25 AUG 2011, 10:45PM</span>
			</li>
			<li>
				<span class="text"><a href="/sale-detail.php">Quantity of Crop</a></span><br/>
				<span class="subtitle">25 AUG 2011, 10:45PM</span>
			</li>
			<li class="pagination"><a href="">&laquo; Prev</a> | <a href="">Next &raquo;</a></li>
		</ul>
		
		<?php include_once('search-include.php'); ?>	
	
		<h2>Menu</h2>
		<?php include_once('menu.php'); ?>		
	</div> <!-- /.content -->

<?php include_once('footer.php'); ?>